# TCP拥塞算法BBR变体

移植到了arch的`linux-zen`或Ubuntu的`liquorix`内核。

## 编译&运行

确保你的系统有`dkms`，内核构建环境和至少有内核头文件。

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

然后任选nanqinlang或tsunami作为拥塞算法:

```
sudo tee -a /etc/sysctl.conf <<< "net.ipv4.tcp_congestion_control = nanqinlang"
```

或
```
sudo tee -a /etc/sysctl.conf <<< "net.ipv4.tcp_congestion_control = tsunami"
```

或
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
