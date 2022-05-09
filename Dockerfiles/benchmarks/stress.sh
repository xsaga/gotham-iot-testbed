
containername="clever_fermi"

# nmon -f -s 1 -c 5000
# grep "CPU002" *.nmon

for cpulimit in $(seq 0.1 0.1 1 | tr "," ".")
do
    docker update --cpus="${cpulimit}" --cpuset-cpus "1" ${containername}
    docker inspect ${containername} --format='{{.HostConfig.NanoCpus}}'
    docker inspect ${containername} --format='{{.HostConfig.CpusetCpus}}'
    sleep 1
    for i in {1..11..1}
    do
	echo "--> CPU LIMIT: ${cpulimit} ITER: ${i}"
	docker container exec ${containername} stress-ng --cpu 0 -t 30 --metrics --log-brief
    done
    sleep 9
done
