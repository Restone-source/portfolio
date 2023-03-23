만약 아래와 같이 CUDA를 확인 할수 없으면
# [wongi@WONGPU ~]$ nvcc --version
# -bash: nvcc: command not found

ls /usr/local/ | grep cuda

cuda
cuda-11
cuda-11.8

sudo sh -c "echo 'export PATH=$PATH:/usr/local/cuda-11.8/bin' >> /etc/profile"
sudo sh -c "echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-11.8/lib64' >> /etc/profile"
sudo sh -c "echo 'export CUDADIR=/usr/local/cuda-11.8' >> /etc/profile"
source /etc/profile





