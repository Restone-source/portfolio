#테스트용 명령어 n 은 코어 N은 노드 갯수 지정
sbatch -n 3 start.sh
sbatch -N 2 start.sh
#작업 취소
scancel 4

#작업 상태 확인 https://slurm.schedmd.com/squeue.html 를 참고할 것.
squeue
squeue -o "%.18i %Q %.9q %.8j %.8u %.10a %.2t %.10M %.10L %.6C %R" | more
scontrol show job

#노드 상태확인
sinfo --format="%9P %l %10n %.14C %.10T"
sinfo -p hpc --format="%9P %l %10n %.14C %.10T"

# 작업 PD (펜딩) 일 때
squeue --start


scontrol show config | grep "ResumeTimeout"

sudo systemctl restart slurmctld

scontrol show node 