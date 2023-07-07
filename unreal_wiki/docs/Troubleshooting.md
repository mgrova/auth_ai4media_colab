
# Troubleshooting

## Incompatible or missing module Airsim

When, after adding the airsim plugin to our project we get the following pop-up:

*TODO: Add pop-up image*

The project should be recompiled as follows:

```
<unreal_path>/Engine/Binaries/ThirdParty/Mono/Linux/bin/mono <unreal_path>/Engine/Binaries/DotNET/UnrealBuildTool.exe Development Linux -Project=<Project_Folder>/<Project_Name>.uproject -TargetType=Editor -Progress
```

Solution taken from following [link](https://github.com/microsoft/AirSim/issues/4535).

Note that this solution can also be extrapolated whenever a project module needs to be recompiled.

## Building executable for Linux systems

```
LogStreaming: Error: Couldn't find file for package /AirSim/Blueprints/BP_FlyingPawn requested by async loading code. NameToLoad: /AirSim/Blueprints/BP_FlyingPawn
```

To solve this problem when compiling the scenario, follow the following [GitHub answer](https://github.com/microsoft/AirSim/issues/1310#issuecomment-427309361).
