# TCP拥塞算法BBR变体

[liquorix内核介绍](https://www.sysgeek.cn/liquorix-kernel/)

移植了以下BBR算法变体到arch的`linux-zen`或Ubuntu的`liquorix`内核:

* [nanqinlang](https://github.com/tcp-nanqinlang)
* [tsunami](https://github.com/KozakaiAya/TCP_BBR/blob/master/code/v6.1/tcp_tsunami.c)
* [bbrplus](https://github.com/cx9208/bbrplus)

## 选择算法

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

ss -tin|grep -E 'nanqinlang|tsunami|bbrplus'
```

## 固化到系统

```
sudo tee -a /etc/modules-load.d/tcp-cong.conf <<< tcp_nanqinlang
sudo tee -a /etc/modules-load.d/tcp-cong.conf <<< tcp_tsunami
sudo tee -a /etc/modules-load.d/tcp-cong.conf <<< tcp_bbrplus
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

成功后，重启即可:

```
sudo reboot
```

如果你由于缺乏bpf、vmlinux等原因插入模块失败，显示:

```
missing module BTF, cannot register kfuncs
```

此时，应用以下补丁:

```
diff --git a/tcp_nanqinlang.c b/tcp_nanqinlang.c
index a8f42e3..80d3317 100644
--- a/tcp_nanqinlang.c
+++ b/tcp_nanqinlang.c
@@ -1204,13 +1204,8 @@ static const struct btf_kfunc_id_set tcp_bbr_kfunc_set = {
 
 static int __init bbr_register(void)
 {
-       int ret;
-
        BUILD_BUG_ON(sizeof(struct bbr) > ICSK_CA_PRIV_SIZE);
 
-       ret = register_btf_kfunc_id_set(BPF_PROG_TYPE_STRUCT_OPS, &tcp_bbr_kfunc_set);
-       if (ret < 0)
-               return ret;
        return tcp_register_congestion_control(&tcp_bbr_cong_ops);
 }
 
diff --git a/tcp_tsunami.c b/tcp_tsunami.c
index 2c72226..b55f19a 100644
--- a/tcp_tsunami.c
+++ b/tcp_tsunami.c
@@ -1205,13 +1205,8 @@ static const struct btf_kfunc_id_set tcp_bbr_kfunc_set = {
 
 static int __init bbr_register(void)
 {
-       int ret;
-
        BUILD_BUG_ON(sizeof(struct bbr) > ICSK_CA_PRIV_SIZE);
 
-       ret = register_btf_kfunc_id_set(BPF_PROG_TYPE_STRUCT_OPS, &tcp_bbr_kfunc_set);
-       if (ret < 0)
-               return ret;
        return tcp_register_congestion_control(&tcp_bbr_cong_ops);
 }
```

然后重新构建：

```
sudo make dkms-remove
sudo make dkms
```
