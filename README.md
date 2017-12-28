## SPP Container

## Install

* docker-compose

## How to run docker without sudo

You need to run docker with sudo because docker daemon binds to a unix socket instead of a TCP port.
Unix socket is owned by root and other users can only access it using sudo.

However, you can run if you add your account to docker group.

```sh
$ sudo groupadd docker
$ sudo usermod -aG docker $USER
```

To activate it, logout and re-login at once.
