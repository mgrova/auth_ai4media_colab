# Research project

TBC

## Look-Outside-Room

First of all, its neccesary to train the first stage of this architecture, that is based in VQ-GAN encoder-decoder.

### Obtain first stage trained model on custom dataset

Follow this guide: https://github.com/CompVis/taming-transformers#training-on-custom-data.

Dont forget to modify the [model config file](https://github.com/CompVis/taming-transformers/blob/master/configs/custom_vqgan.yaml) with lookout embedding dimension and path to out dataset. 

```
model:
  base_learning_rate: 4.5e-6
  target: taming.models.vqgan.VQModel
  params:
    embed_dim: 256
    n_embed: 16384
    ddconfig:
      double_z: False
      z_channels: 256
      resolution: 256
      in_channels: 3
      out_ch: 3
      ch: 128
      ch_mult: [ 1,1,2,2,4]  # num_down = len(ch_mult)-1
      num_res_blocks: 2
      attn_resolutions: [16]
      dropout: 0.0

    lossconfig:
      target: taming.modules.losses.vqperceptual.VQLPIPSWithDiscriminator
      params:
        disc_conditional: False
        disc_in_channels: 3
        disc_start: 10000
        disc_weight: 0.8
        codebook_weight: 1.0

data:
  target: main.DataModuleFromConfig
  params:
    batch_size: 3
    num_workers: 8
    train:
      target: taming.data.custom.CustomTrain
      params:
        training_images_list_file: /home/aiiacvmllab/Documents/datasets/LookOut_UE4/train.txt
        size: 256
    validation:
      target: taming.data.custom.CustomTest
      params:
        test_images_list_file: /home/aiiacvmllab/Documents/datasets/LookOut_UE4/test.txt
        size: 256
```

To train the model, run the following command (with propper config file, name and GPU index):
```
python main.py --base configs/custom_vqgan_lookout.yaml --name custom_piramids -t True --gpus 2,
```