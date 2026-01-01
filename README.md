# TCP拥塞算法BBR变体

[liquorix内核介绍](https://www.sysgeek.cn/liquorix-kernel/)

移植了以下BBR算法变体到arch的`linux-zen`或Ubuntu的`liquorix`内核:

* [nanqinlang](https://github.com/tcp-nanqinlang)
* [tsunami](https://github.com/KozakaiAya/TCP_BBR/blob/master/code/v6.1/tcp_tsunami.c)
* [bbrplus](https://github.com/cx9208/bbrplus)
* [bbr1](https://github.com/torvalds/linux/blob/master/net/ipv4/tcp_bbr.c)

## 选择算法

需要注意的是，一些发行版内核（例如 **linux-zen**、较新的 **liquorix** 内核等）已经将内核自带的 `bbr` 实现替换为 **BBRv3**，而不再是最初的 BBRv1。

这意味着：

- 系统中看到的 `bbr` 拥塞控制算法，实际行为可能是 **BBRv3**
- 本项目中的 `bbr1` 明确对应 **原始 BBRv1** 实现，用于对比测试或兼容旧行为
- `bbrplus`、`nanqinlang`、`tsunami` 等均是基于 BBRv1/早期 BBR 思路的改进算法，与 BBRv3 的设计目标和实现细节存在明显差异
- `tcp_bbr1`模块的tcp拥塞算法名字需要改为`bbr1`

**使用提醒**：在实际使用中，BBRv3 在 **高 RTT / 高丢包** 的复杂网络环境（例如翻墙、跨境链路）下，吞吐和稳定性表现往往较差，不少用户反馈其带宽利用率明显低于 BBRv1 系变体。因此，**翻墙或跨境 VPS 场景不建议使用内核自带的 `bbr`（BBRv3）**，而更适合选择 `bbrplus`、`bbr1` 等算法进行测试和部署。


根据[论文](https://arxiv.org/abs/1909.03673)的评测，应该选择`bbrplus`:

```
BBRPlus is an good improvement to BBR and is highly recommended to be applied in this paper
```

你也可以根据自己需要选用其它算法。

## 编译&运行

以Ubuntu 22.04.03 LTS amd64为例：
确保你的系统有`dkms`，内核构建环境和至少有内核头文件。(Ubuntu下叫 `linux-headers-liquorix-amd64`)

```
sudo apt install -y git build-essential dkms linux-headers-liquorix-amd64
git clone https://github.com/hrimfaxi/tcp_bbr_modules
cd tcp_bbr_modules
```

```
sudo make dkms
sudo modprobe tcp_nanqinlang
sudo modprobe tcp_tsunami
sudo modprobe tcp_bbrplus

# 试用nanqinlang
sudo sysctl -w net.ipv4.tcp_congestion_control=nanqinlang

# 试用tsunami
sudo sysctl -w net.ipv4.tcp_congestion_control=tsunami

# 试用bbrplus
sudo sysctl -w net.ipv4.tcp_congestion_control=bbrplus

# 试用bbr1
sudo sysctl -w net.ipv4.tcp_congestion_control=bbr1

ss -tin|grep -E 'nanqinlang|tsunami|bbrplus|bbr1'
```

## 固化到系统

```
sudo tee -a /etc/modules-load.d/tcp-cong.conf <<< tcp_nanqinlang
sudo tee -a /etc/modules-load.d/tcp-cong.conf <<< tcp_tsunami
sudo tee -a /etc/modules-load.d/tcp-cong.conf <<< tcp_bbrplus
sudo tee -a /etc/modules-load.d/tcp-cong.conf <<< tcp_bbr1
```

然后任选一个算法作为拥塞算法:

nanqinlang:
```
sudo tee -a /etc/sysctl.conf <<< "net.ipv4.tcp_congestion_control = nanqinlang"
```

tsunami:
```
sudo tee -a /etc/sysctl.conf <<< "net.ipv4.tcp_congestion_control = tsunami"
```

bbrplus:
```
sudo tee -a /etc/sysctl.conf <<< "net.ipv4.tcp_congestion_control = bbrplus"
```

bbr1:
```
sudo tee -a /etc/sysctl.conf <<< "net.ipv4.tcp_congestion_control = bbr1"
```

成功后，重启即可:

```
sudo reboot
```
