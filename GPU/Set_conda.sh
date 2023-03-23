# Use Unbuntu HPC Image

# Python Version select 이거 안해도 됨
# ls /usr/bin/ | grep python
# sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
# sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 2
# sudo update-alternatives --config python

# Anaconda install [ Check login user ] 
wget https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh    # 최신버전 확인해볼것
bash Anaconda3-2022.05-Linux-x86_64.sh # 조금 걸림
# init 설정시 - yes # 이거 안하면 다음 bashrc 실행해도 conda 가 alias 적용 안됨.
source ~/.bashrc

# base 환경이 만들어짐.
# 각종 오류를 회피하려면 conda를 업데이트 후 새 환경을 만든다.

# Conda update
conda update --all

# Create env
conda create -n newenv

# Change env
source activate newenv
# or
conda activate newenv

# Check env
conda info --envs

# 파이토치 테스트를 위한 세팅
# Pytorch install
conda install pytorch torchvision torchaudio cpuonly -c pytorch

# Pytorch check
python

# 각종 확인 명령어
import torch
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(torch.cuda.current_device()))
torch.zeros(1).cuda()

# 추가 참고용 명령어들
# 환경 내 설치된 패키지 확인 (ex. torch)
conda list | grep torch

# 인터페이스 확인 # 사용중일 때 나타남
nvidia-smi

# GPU Hardware reset # 안해봐서 어떨지 모름
nvidia-smi -r