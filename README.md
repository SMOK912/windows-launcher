# Windows Launcher

I wanted a tool to use for this purpose, and I made it. I put it here for anyone else who may need/want it :3

## Theming and Customization

Without modifying the functionality (`launcher.ps1`), or building/compiling anything, you can just edit the window.xaml, apps.json, and icons in the `icons` folder to customize the launcher for whatever you need.

To change general coloring, you can go into `window.xaml`, and change `Background=""` and `Foreground=""` attributes.
The only exception to that is the `Setter`: `<Setter TargetName="border" Property="Background" Value="#e81123" />`, which is self explanatory on how to handle and alter it.

### Icons

Preferably use `.ico` files, since I only implemented support for them, and I don't know if any other file format will work.
