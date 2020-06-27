sudo chmod o+wt '/sys/fs/cgroup/blkio/'
sudo chmod o+wt '/sys/fs/cgroup/cpu,cpuacct/'
sudo chmod o+wt '/sys/fs/cgroup/freezer/'
sudo chmod o+wt /sys/fs/cgroup/cpuset
sudo chmod o+wt /sys/fs/cgroup/blkio/ /sys/fs/cgroup/cpu,cpuacct/ /sys/fs/cgroup/freezer/ /sys/fs/cgroup/memory/user.slice/user-1000.slice/session-1.scope
#--tasks ReachSafety-Arrays 
benchexec ./testcov.xml --timelimit 900s --tasks ReachSafety-Arrays --limitCores 1 --numOfThreads 1 --no-container --no-compress-results
