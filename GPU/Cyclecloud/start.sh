#!/bin/bash

#SBATCH -J antjob   # job name
#SBATCH -o antjob.%j.out   # standard output and error log
#SBATCH -p hpc           # queue  name  or  partiton name

##mpiexec hostname |sort
mpirun hostname |sort
##srun hostname |sort