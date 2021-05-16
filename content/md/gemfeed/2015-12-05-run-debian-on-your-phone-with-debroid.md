# Run Debian on your phone with Debroid

```
 ____       _               _     _ 
|  _ \  ___| |__  _ __ ___ (_) __| |
| | | |/ _ \ '_ \| '__/ _ \| |/ _` |
| |_| |  __/ |_) | | | (_) | | (_| |
|____/ \___|_.__/|_|  \___/|_|\__,_|
                                    
```

> Written by Paul Buetow 2015-12-05, last updated 2021-05-16

You can use the following tutorial to install a full-blown Debian GNU/Linux Chroot on a LG G3 D855 CyanogenMod 13 (Android 6). First of all you need to have root permissions on your phone and you also need to have the developer mode activated. The following steps have been tested on Linux (Fedora 23).

[![./2015-12-05-run-debian-on-your-phone-with-debroid/Deboroid.png](./2015-12-05-run-debian-on-your-phone-with-debroid/Deboroid.png)](./2015-12-05-run-debian-on-your-phone-with-debroid/Deboroid.png)  

## Foreword

A couple of years have passed since I last worked on Debroid. At the moment I am using the Termux app on Android, which is less sophisticated than a fully blown Debian installation, but sufficient for my current requirements.

## Step by step guide

All scripts mentioned here can be found on GitHub at:

[https://github.com/snonux/debroid](https://github.com/snonux/debroid)  

### First debootstrap stage

This is to be performed on a Fedora Linux machine (could work on a Debian too, but Fedora is just what I use on my personal Laptop). The following steps prepare an initial Debian base image, which then later can be transferred to the phone.

```code
sudo dnf install debootstrap
# 5g
dd if=/dev/zero of=jessie.img bs=$[ 1024 * 1024 ] \
  count=$[ 1024 * 5 ]

# Show used loop devices
sudo losetup -f
# Store the next free one to $loop
loop=loopN
sudo losetup /dev/$loop jessie.img

mkdir jessie
sudo mkfs.ext4 /dev/$loop
sudo mount /dev/$loop jessie
sudo debootstrap --foreign --variant=minbase \
  --arch armel jessie jessie/ \
  http://http.debian.net/debian
sudo umount jessie
```

### Copy Debian image to the phone

Now setup the Debian image on an external SD card on the Phone via Android Debugger as follows:

```
adb root && adb wait-for-device && adb shell
mkdir -p /storage/sdcard1/Linux/jessie
exit

# Sparse image problem, may be too big for copying otherwise
gzip jessie.img
# Copy over
adb push jessie.img.gz /storage/sdcard1/Linux/jessie.img.gz
adb shell
cd /storage/sdcard1/Linux
gunzip jessie.img.gz

# Show used loop devices
losetup -f
# Store the next free one to $loop
loop=loopN

# Use the next free one (replace the loop number)
losetup /dev/block/$loop $(pwd)/jessie.img
mount -t ext4 /dev/block/$loop $(pwd)/jessie

# Bind-Mound proc, dev, sys`
busybox mount --bind /proc $(pwd)/jessie/proc
busybox mount --bind /dev $(pwd)/jessie/dev
busybox mount --bind /dev/pts $(pwd)/jessie/dev/pts
busybox mount --bind /sys $(pwd)/jessie/sys

# Bind-Mound the rest of Android
mkdir -p $(pwd)/jessie/storage/sdcard{0,1}
busybox mount --bind /storage/emulated \
  $(pwd)/jessie/storage/sdcard0
busybox mount --bind /storage/sdcard1 \
  $(pwd)/jessie/storage/sdcard1

# Check mounts
mount | grep jessie
```

### Second debootstrap stage

This is to be performed on the Android phone itself (inside a Debian chroot):

```
chroot $(pwd)/jessie /bin/bash -l
export PATH=/bin:/usr/bin:/usr/local/bin:/sbin:/usr/sbin:/usr/local/sbin
/debootstrap/debootstrap --second-stage
exit # Leave chroot
exit # Leave adb shell
```

### Setup of various scripts

jessie.sh deals with all the loopback mount magic and so on. It will be run later every time you start Debroid on your phone.

```
# Install script jessie.sh
adb push storage/sdcard1/Linux/jessie.sh /storage/sdcard/Linux/jessie.sh
adb shell
cd /storage/sdcard1/Linux
sh jessie.sh enter

# Bashrc
cat <<END >~/.bashrc
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH
export EDITOR=vim
hostname $(cat /etc/hostname)
END

# Fixing an error message while loading the profile
sed -i s#id#/usr/bin/id# /etc/profile

# Setting the hostname
echo phobos > /etc/hostname
echo 127.0.0.1 phobos > /etc/hosts
hostname phobos

# Apt-sources
cat <<END > sources.list
deb http://ftp.uk.debian.org/debian/ jessie main contrib non-free
deb-src http://ftp.uk.debian.org/debian/ jessie main contrib non-free
END
apt-get update
apt-get upgrade
apt-get dist-upgrade
exit # Exit chroot
```

### Entering Debroid and enable a service

This enters Debroid on your phone and starts the example service uptimed:

```
sh jessie.sh enter

# Setup example serice uptimed
apt-get install uptimed
cat <<END > /etc/rc.debroid
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH
service uptimed status &>/dev/null || service uptimed start
exit 0
END

chmod 0755 /etc/rc.debroid
exit # Exit chroot
exit # Exit adb shell
```

### Include to Android startup:

I you want to start Debroid automatically every time when your phone starts, then do the following:

```
adb push data/local/userinit.sh /data/local/userinit.sh
adb shell
chmod +x /data/local/userinit.sh
exit
```

Reboot & test!  Enjoy!

E-Mail me your thoughts at comments@mx.buetow.org!

[Go back to the main site](../)  
