#!/bin/bash

sh build.sh
cp ./bin/CodeCraft-2021.exe ../data/Finall/bin/chier.exe
cd ../data/Finall

bin_name=chier.exe

# python simulation.py training-1.txt -- ./bin/$bin_name -- ./bin/zero.exe
# python simulation.py training-2.txt -- ./bin/$bin_name -- ./bin/zero.exe
# python simulation.py training-3.txt -- ./bin/$bin_name -- ./bin/zero.exe
# python simulation.py training-4.txt -- ./bin/$bin_name -- ./bin/zero.exe

# python simulation.py training-1.txt -- ./bin/$bin_name -- ./bin/31.exe
# python simulation.py training-2.txt -- ./bin/$bin_name -- ./bin/31.exe
# python simulation.py training-3.txt -- ./bin/$bin_name -- ./bin/31.exe
# python simulation.py training-4.txt -- ./bin/$bin_name -- ./bin/31.exe

# python simulation.py training-1.txt -- ./bin/$bin_name -- ./bin/F-421v2.exe
# python simulation.py training-2.txt -- ./bin/$bin_name -- ./bin/F-421v2.exe
# python simulation.py training-3.txt -- ./bin/$bin_name -- ./bin/F-421v2.exe
# python simulation.py training-4.txt -- ./bin/$bin_name -- ./bin/F-421v2.exe

# python simulation.py training-1.txt -- ./bin/$bin_name -- ./bin/fltt.exe
# python simulation.py training-2.txt -- ./bin/$bin_name -- ./bin/fltt.exe
# python simulation.py training-3.txt -- ./bin/$bin_name -- ./bin/fltt.exe
# python simulation.py training-4.txt -- ./bin/$bin_name -- ./bin/fltt.exe

python simulation.py training-1.txt -- ./bin/$bin_name -- ./bin/magicraft_419.exe
# python simulation.py training-2.txt -- ./bin/$bin_name -- ./bin/magicraft_419.exe
# python simulation.py training-3.txt -- ./bin/$bin_name -- ./bin/magicraft_419.exe
# python simulation.py training-4.txt -- ./bin/$bin_name -- ./bin/magicraft_419.exe
