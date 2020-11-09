#! /bin/bash

str=$( curl -s https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt | perl -MList::Util=shuffle -e 'print shuffle<STDIN>' | head | tr '\n' ' ' | sed -E 's/\b\(\w\)\{,4\}\b\s*//g' | awk '{print $1" "$2" "$3" "$4;}' )
sudo echo "serverpi_access_key = $str" > /root/.serverpi
ssh-keygen -q -t rsa -N "${str}" -f /root/.ssh/id_rsa
ssh-copy-id -i /root/.ssh/id_rsa serverpi@10.3.141.1
