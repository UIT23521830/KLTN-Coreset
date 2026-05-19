$repos = @(
    "https://github.com/avivhadar33/coretab.git",
    "https://github.com/for0nething/RECON.git",
    "https://github.com/teddy4445/SubStrat.git",
    "https://github.com/baharanm/craig.git",
    "https://github.com/decile-team/cords.git",
    "https://github.com/dssresearch/GLISTER.git",
    "https://github.com/allenai/cartography.git",
    "https://github.com/mtoneva/example_forgetting.git",
    "https://github.com/stanford-futuredata/selection-via-proxy.git",
    "https://github.com/tmllab/2023_ICLR_Moderate-DS.git",
    "https://github.com/VICO-UoE/DatasetCondensation.git",
    "https://github.com/Sssara-5/TF-TabularCondensation.git",
    "https://github.com/inwonakng/tdbench.git"
)

New-Item -ItemType Directory -Force -Path "sota_repos" | Out-Null
Set-Location "sota_repos"

foreach ($repo in $repos) {
    $folderName = ($repo -split "/")[-1].Replace(".git", "")
    if (-Not (Test-Path $folderName)) {
        Write-Host "Cloning $folderName..."
        git clone --depth 1 $repo
    } else {
        Write-Host "$folderName already exists, skipping."
    }
}
Write-Host "All repositories cloned."
