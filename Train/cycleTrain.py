import torch
from Util.dataset import GraffitiTextDataset
# from Util.utils import save_checkpoint, load_checkpoint
from torch.utils.data import DataLoader
import torch.nn as nn
import torch.optim as optim
from Util import config
from tqdm import tqdm
from torchvision.utils import save_image
from Util.discriminator import Discriminator
from Util.generator import Generator
from Util.utils import save_checkpoint, load_checkpoint, reverseNormalization

def train_fn(disc_G, disc_T, gen_G, gen_T, loader, opt_disc, opt_gen, l1, mse, d_scaler, g_scaler):
    H_reals = 0
    H_fakes = 0
    loop = tqdm(loader, leave=True)

    for idx, (graff, text) in enumerate(loop):
        graff = graff.to(config.DEVICE)
        text = text.to(config.DEVICE)

        # Train Discriminators H and Z
        with torch.cuda.amp.autocast():
            fake_graff = gen_G(text)
            D_G_real = disc_G(graff)
            D_G_fake = disc_G(fake_graff.detach())
            D_G_real_loss = mse(D_G_real, torch.ones_like(D_G_real))
            D_G_fake_loss = mse(D_G_fake, torch.zeros_like(D_G_fake))
            D_G_loss = D_G_real_loss + D_G_fake_loss

            fake_text = gen_T(graff)
            D_T_real = disc_T(text)
            D_T_fake = disc_T(fake_text.detach())
            D_T_real_loss = mse(D_T_real, torch.ones_like(D_T_real))
            D_T_fake_loss = mse(D_T_fake, torch.zeros_like(D_T_fake))
            D_T_loss = D_T_real_loss + D_T_fake_loss

            # put it togethor
            D_loss = (D_G_loss + D_T_loss)/2

        opt_disc.zero_grad()
        d_scaler.scale(D_loss).backward()
        d_scaler.step(opt_disc)
        d_scaler.update()

        # Train Generators G and T
        with torch.cuda.amp.autocast():
            # adversarial loss for both generators
            D_G_fake = disc_G(fake_graff)
            D_T_fake = disc_T(fake_text)
            loss_G_G = mse(D_G_fake, torch.ones_like(D_G_fake))
            loss_G_T = mse(D_T_fake, torch.ones_like(D_T_fake))

            # cycle loss
            cycle_graff = gen_G(fake_text)
            cycle_text = gen_T(fake_graff)
            cycle_graff_loss = l1(graff, cycle_graff)
            cycle_text_loss = l1(text, cycle_text)

            # identity loss (remove these for efficiency if you set lambda_identity=0)
            identity_graff = gen_G(graff)
            identity_text = gen_T(text)
            identity_graff_loss = l1(graff, identity_graff)
            identity_text_loss = l1(text, identity_text)

            # add all togethor
            G_loss = (
                    loss_G_G
                    + loss_G_T
                    + cycle_graff_loss * config.LAMBDA_CYCLE
                    + cycle_text_loss * config.LAMBDA_CYCLE
                    + identity_graff_loss * config.LAMBDA_IDENTITY
                    + identity_text_loss * config.LAMBDA_IDENTITY
            )

        opt_gen.zero_grad()
        g_scaler.scale(G_loss).backward()
        g_scaler.step(opt_gen)
        g_scaler.update()

        if idx % 200 == 0:
            # reverse normalization
            save_image(reverseNormalization(fake_graff,0.5,0.5), f"saved_images/graff_{idx}.png")
            save_image(reverseNormalization(fake_text,0.5,0.5), f"saved_images/text_{idx}.png")

        loop.set_postfix(H_real=H_reals/(idx+1), H_fake=H_fakes/(idx+1))



def main():
    # Discriminator
    disc_G = Discriminator(in_channels=1).to(config.DEVICE)
    disc_T = Discriminator(in_channels=1).to(config.DEVICE)
    # Generator
    gen_G = Generator(img_channels=1, num_residuals=9).to(config.DEVICE)
    gen_T = Generator(img_channels=1, num_residuals=9).to(config.DEVICE)
    opt_disc = optim.Adam(
        list(disc_G.parameters()) + list(disc_T.parameters()),
        lr=config.LEARNING_RATE,
        betas=(0.5, 0.999),
    )

    opt_gen = optim.Adam(
        list(gen_G.parameters()) + list(gen_T.parameters()),
        lr=config.LEARNING_RATE,
        betas=(0.5, 0.999),
    )

    L1 = nn.L1Loss()
    mse = nn.MSELoss()

    if config.LOAD_MODEL:
        load_checkpoint(
            config.CHECKPOINT_GEN_G, gen_G, opt_gen, config.LEARNING_RATE,
        )
        load_checkpoint(
            config.CHECKPOINT_GEN_T, gen_T, opt_gen, config.LEARNING_RATE,
        )
        load_checkpoint(
            config.CHECKPOINT_CRITIC_G, disc_G, opt_disc, config.LEARNING_RATE,
        )
        load_checkpoint(
            config.CHECKPOINT_CRITIC_T, disc_T, opt_disc, config.LEARNING_RATE,
        )

    dataset = GraffitiTextDataset(
        # root_graf="/Users/chenziyang/Documents/Ziyang/GAN/Graffiti Project/GraffitiGan/data/train/Graffiti",
        # root_text="/Users/chenziyang/Documents/Ziyang/GAN/Graffiti Project/GraffitiGan/data/train/Text",
        root_graf="/content/drive/MyDrive/GraffitiGan/data/train/Graffiti",
        root_text="/content/drive/MyDrive/GraffitiGan/data/train/Text",
        transform=config.transforms
    )
    val_dataset = GraffitiTextDataset(
        # root_graf="/Users/chenziyang/Documents/Ziyang/GAN/Graffiti Project/GraffitiGan/data/test/Graffiti",
        # root_text="/Users/chenziyang/Documents/Ziyang/GAN/Graffiti Project/GraffitiGan/data/test/Text",
        root_graf="/content/drive/MyDrive/GraffitiGan/data/test/Graffiti",
        root_text="/content/drive/MyDrive/GraffitiGan/data/test/Text",
        transform=config.transforms
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=1,
        shuffle=False,
        pin_memory=True,
    )
    loader = DataLoader(
        dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=True,
        num_workers=config.NUM_WORKERS,
        pin_memory=True
    )
    g_scaler = torch.cuda.amp.GradScaler()
    d_scaler = torch.cuda.amp.GradScaler()

    for epoch in range(config.NUM_EPOCHS):
        train_fn(disc_G, disc_T, gen_G, gen_T, loader, opt_disc, opt_gen, L1, mse, d_scaler, g_scaler)

        if config.SAVE_MODEL:
            save_checkpoint(gen_G, opt_gen, filename=config.CHECKPOINT_GEN_G)
            save_checkpoint(gen_T, opt_gen, filename=config.CHECKPOINT_GEN_T)
            save_checkpoint(disc_G, opt_disc, filename=config.CHECKPOINT_CRITIC_G)
            save_checkpoint(disc_T, opt_disc, filename=config.CHECKPOINT_CRITIC_T)

if __name__ == "__main__":
    main()