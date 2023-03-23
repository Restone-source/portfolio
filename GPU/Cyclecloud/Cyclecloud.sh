#이미지 urn 찾기
az vm image list --publisher "microsoft-dsvm" --all -o table --offer ubuntu-hpc --sku 1804
#기본
microsoft-dsvm:ubuntu-hpc:1804:latest


az vm image list --publisher "microsoft-dsvm" --all -o table # --offer ubuntu-hpc --sku 1804
