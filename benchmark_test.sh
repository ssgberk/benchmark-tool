#!/bin/bash
./ssgberk --clean
clear &&  clear
# 1-05-10
./ssgberk -nf 10      -cs 0.500   -mr 10

# 2-05-10
./ssgberk -nf 100     -cs 0.500   -mr 10

# 3-05-10
./ssgberk -nf 1000    -cs 0.500   -mr 10

# 4-05-10
./ssgberk -nf 10000   -cs 0.500   -mr 10

# 1-1K-10
./ssgberk -nf 10      -cs 1000    -mr 10

# 1-5K-10
./ssgberk -nf 10      -cs 5000    -mr 10

# 5-05-10
./ssgberk -nf 100000  -cs 0.500   -mr 10
: '
# 1-10K-10
./ssgberk -nf 10      -cs 10000   -mr 10

# 2-1K-10
./ssgberk -nf 100     -cs 1000    -mr 10

# 2-5K-10
./ssgberk -nf 100     -cs 5000    -mr 10

# 6-05-10
./ssgberk -nf 1000000 -cs 0.500   -mr 10

# 6A-05-3
./ssgberk -nf 1800000 -cs 0.500   -mr 3

# 3A-1K-3
./ssgberk -nf 900     -cs 1000    -mr 3

# 2A-5K-3
./ssgberk -nf 180     -cs 5000    -mr 3

# 2A-10K-3
./ssgberk -nf 90      -cs 10000   -mr 3
'