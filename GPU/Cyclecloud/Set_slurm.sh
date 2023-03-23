############### slurm cluster ################## 

##### Scheduler node set #####

# MPIRUN Setting
# dpkg -l | grep mpi
# find /usr -name "mpirun"
export PATH=$PATH:/usr/mpi/gcc/openmpi-4.1.4rc1/bin/
