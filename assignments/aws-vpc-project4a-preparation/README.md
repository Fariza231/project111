# Project 4a — две VPC и две реальные терминальные сессии

Это инструкция подготовки, а не выполненная лабораторная и не журнал подключения. Для сдачи нужны два TXT-файла с настоящим выводом вашей AWS-лаборатории. Не загружайте эту инструкцию вместо них.

## Доступ и исходные материалы

1. Откройте AWS Academy Learner Lab, нажмите Start Lab и дождитесь готовности, затем откройте AWS Console.
2. Используйте регион us-east-1 (N. Virginia), где по Project 1a преподаватель публикует образ курса.
3. Найдите актуальный образ курса, разрешённый в вашей лаборатории. В двух PDF указаны разные имена образов (`coursera_cs5910a_im1` и `coursera_cs5910_im2`); наличие и актуальный AMI нужно проверить в своей Academy. Если образ отсутствует, уточните его у преподавателя; не подменяйте его незаметно другой системой.
4. Создайте/выберите key pair и сохраните PEM только на своём компьютере. Никому не отправляйте приватный ключ или значения AWS access/secret/session keys в чат или GitHub.

## 1. Создайте сети: VPC → Create VPC → VPC only

| Ресурс | Название | IPv4 CIDR |
|---|---|---|
| DMZ VPC | lab_dmz | 172.16.123.0/24 |
| Intranet VPC | lab_intra | 10.0.0.0/16 |
| Подсеть в DMZ VPC | lab_dmz_subnet | 172.16.123.0/24 |
| Подсеть в Intranet VPC | lab_intra_subnet | 10.0.0.0/24 |

Подсеть Intranet /24 — выбранный поддиапазон VPC /16; адреса примеров PDF попадают в него. Обе подсети разместите в одной Availability Zone: дополнительный ENI можно присоединить только к экземпляру в той же AZ. Отключите Auto-assign public IPv4 в настройках подсетей.

## 2. Создайте Internet Gateway

VPC → Internet gateways → Create → имя lab_dmz_igw → Attach to VPC → lab_dmz. Не присоединяйте IGW к Intranet.

## 3. Создайте и примите peering

VPC → Peering connections → Create: requester = lab_dmz, accepter = lab_intra, ваш аккаунт и тот же регион. После создания Actions → Accept request. Статус должен стать Active.

## 4. Настройте маршруты и явные ассоциации подсетей

Создайте/выберите отдельную route table в каждой VPC; убедитесь, что нужная подсеть связана с ней через Subnet associations.

DMZ route table:

| Destination | Target |
|---|---|
| 172.16.123.0/24 | local (автоматически) |
| 10.0.0.0/16 | ваш pcx-ID |
| 0.0.0.0/0 | ваш igw-ID |

Intranet route table:

| Destination | Target |
|---|---|
| 10.0.0.0/16 | local (автоматически) |
| 172.16.123.0/24 | тот же pcx-ID |

Не добавляйте default route из Intranet в pcx ради интернета: peering не поддерживает транзит к IGW другой VPC. Для требуемых отдельных SSH-соединений через jump hosts NAT и IP forwarding не нужны. Сама по себе эта конфигурация не принуждает произвольный трафик проходить Linux firewall: это отдельная задача маршрутизации/фильтрации.

## 5. Создайте четыре EC2-экземпляра

Используйте разрешённый в лаборатории тип экземпляра с поддержкой двух ENI для fwout/fwin, один образ курса и один key pair. Имена интерфейсов Linux могут отличаться от eth0/eth1; проверяйте `ip -br address`.

| EC2 | VPC / subnet | Пример private IPv4 | ENI | Public IPv4 |
|---|---|---|---|---|
| fwout | lab_dmz / lab_dmz_subnet | основной .10, дополнительный .11 | 2 | Только здесь: Elastic IP на основном ENI |
| ws | lab_dmz / lab_dmz_subnet | 172.16.123.20 | 1 | Нет |
| fwin | lab_intra / lab_intra_subnet | основной 10.0.0.10, дополнительный 10.0.0.11 | 2 | Нет |
| intra1 | lab_intra / lab_intra_subnet | 10.0.0.20 | 1 | Нет |

Адреса таблицы — план, не результаты созданной лаборатории. Можно использовать назначенные AWS адреса; тогда подставьте их в команды/SG.

Для дополнительного ENI: EC2 → Network interfaces → Create network interface → нужная подсеть/SG → Create → Actions → Attach → нужный экземпляр. Для fwout: EC2 → Elastic IPs → Allocate → Associate → основной ENI fwout. Проверьте, что у остальных трёх экземпляров поле Public IPv4 пустое.

## 6. Security Groups

Минимальные SSH-правила (TCP 22) для выбранных адресов:

| SG | Разрешённый source |
|---|---|
| fwout | внешний IPv4 вашего компьютера /32 |
| ws | основной private IP fwout /32 |
| fwin | основной private IP fwout /32 |
| intra1 | основной private IP fwin /32 |

Для HTTP/HTTPS fwout добавьте TCP 80/443 с источников, требуемых PDF: ваш внешний IP /32, 172.16.123.0/24 и 10.0.0.0/16. Если нужен HTTP/HTTPS к ws, разрешите соответствующие внутренние источники. Не открывайте SSH всему интернету. Разрешите нужные исходящие соединения: стандартная SG обычно уже разрешает весь outbound, но проверьте фактические правила. Default NACL обычно разрешает трафик; при изменённых NACL нужно также разрешить обратные ephemeral-порты. Правила SG stateful.

## 7. Вариант с локальным OpenSSH — ключ остаётся на вашем компьютере

В `~/.ssh/config` добавьте, заменив все значения в угловых скобках:

```sshconfig
Host lab-fwout
    HostName <FWOUT_PUBLIC_IP>
    User ec2-user
    IdentityFile <LOCAL_PATH_TO_KEY.pem>
    IdentitiesOnly yes

Host lab-ws
    HostName <WS_PRIVATE_IP>
    User ec2-user
    IdentityFile <LOCAL_PATH_TO_KEY.pem>
    IdentitiesOnly yes
    ProxyJump lab-fwout

Host lab-fwin
    HostName <FWIN_PRIVATE_IP>
    User ec2-user
    IdentityFile <LOCAL_PATH_TO_KEY.pem>
    IdentitiesOnly yes
    ProxyJump lab-fwout

Host lab-intra1
    HostName <INTRA1_PRIVATE_IP>
    User ec2-user
    IdentityFile <LOCAL_PATH_TO_KEY.pem>
    IdentitiesOnly yes
    ProxyJump lab-fwout,lab-fwin
```

В Windows файл обычно находится в `C:\Users\<ваш_пользователь>\.ssh\config`; используйте корректный путь IdentityFile, а путь с пробелами заключите в кавычки. В Mac/Linux выполните `chmod 600 <путь_к_ключу.pem>`.

ProxyJump выполняет SSH через нужные промежуточные узлы, но не создаёт вложенные shell prompts как в примере PDF. Логи с `-v` показывают использованный маршрут и реальные подключения; для максимально похожего на PDF оформления можно использовать вариант ниже с вложенными сессиями.

На первом подключении проверьте fingerprint узла по доверенному каналу/EC2-данным перед принятием. Не используйте отключение StrictHostKeyChecking.

## 8. Запись сессий с ProxyJump: Mac/Linux/WSL

Откройте терминал в каталоге, где хотите сохранить логи.

### Deliverable 1 — DMZ

```bash
script Deliverable_1_DMZ.txt
ssh -v lab-fwout
hostname
whoami
ip -br address
ip route
exit
ssh -v lab-ws
hostname
whoami
ip -br address
ip route
exit
exit
```

Последний `exit` завершает `script`, предыдущие закрывают удалённые SSH-сессии. Здесь лог подтверждает доступ к fwout и доступ к ws через fwout, с ключом только на локальном компьютере.

### Deliverable 2 — Intranet

```bash
script Deliverable_2_Intranet.txt
ssh -v lab-fwout
hostname
ip -br address
exit
ssh -v lab-fwin
hostname
whoami
ip -br address
ip route
exit
ssh -v lab-intra1
hostname
whoami
ip -br address
ip route
exit
exit
```

Verbose SSH пишет, через какие proxy/jump hosts проходит соединение; вывод `hostname`/`ip` должен относиться к реальным машинам. Не заменяйте его примером из PDF.

## 9. Вложенные сессии как в PDF — без копирования PEM на сервер

Если нужен именно переход внутри терминала fwout → ws / fwout → fwin → intra1, используйте локальный ssh-agent с ключом. Разрешайте forwarding только для собственных доверенных учебных jump hosts: они получают доступ к агенту на время сессии. На Mac/Linux:

```bash
eval "$(ssh-agent -s)"
ssh-add <LOCAL_PATH_TO_KEY.pem>
```

Deliverable 1:

```bash
script Deliverable_1_DMZ.txt
ssh -A lab-fwout
hostname
ip -br address
ssh ec2-user@<WS_PRIVATE_IP>
hostname
whoami
ip -br address
ip route
exit
exit
exit
```

Deliverable 2:

```bash
script Deliverable_2_Intranet.txt
ssh -A lab-fwout
hostname
ip -br address
ssh -A ec2-user@<FWIN_PRIVATE_IP>
hostname
ip -br address
ip route
ssh ec2-user@<INTRA1_PRIVATE_IP>
hostname
whoami
ip -br address
ip route
exit
exit
exit
exit
```

После окончания завершите использованный локальный агент командой `ssh-agent -k`, если запустили его именно для этой работы. Этот вариант наиболее близок к двум примерам сессий в PDF и не требует копировать приватный PEM на fwout/fwin.

## 10. Если используете Windows без WSL

В Bitvise SSH Client включите запись терминальной сессии средствами клиента, а для nested SSH потребуется настроить локальный агент/forwarding. Либо установите/откройте WSL и примените команды `script` выше. Не рассчитывайте только на PowerShell Start-Transcript: захват вывода интерактивных native-программ может зависеть от версии и способа запуска. Перед сдачей откройте итоговый TXT и проверьте, что он содержит команды и ответы удалённых машин, а не только запуск ssh.

## 11. Что сдавать

Project Title: `AWS VPC Peering — DMZ and Intranet SSH Connectivity`

- В первое поле: `Deliverable_1_DMZ.txt` с реальным доступом local → fwout → ws.
- Во второе поле: `Deliverable_2_Intranet.txt` с реальным доступом local → fwout → fwin → intra1.

Перед сдачей убедитесь, что логи содержат успешные shell prompts/hostname и адреса, нет ошибок Permission denied/timeout, нет приватного ключа/паролей/access keys. Не удаляйте факты, необходимые для доказательства маршрута. При необходимости приложите/запишите отдельную проверку AWS Console: два CIDR, Active peering, IGW только в DMZ, правильные route-table associations и отсутствие public IP у трёх внутренних узлов.

Реальные результаты AWS здесь не создавались: доступ к вашему AWS Academy в этой среде не настроен.

## Диагностика

- Timeout до fwout: проверьте running/status checks, Elastic IP, маршрут 0/0 → IGW, inbound SSH с актуального внешнего IP /32 и локальную сеть.
- Timeout до fwin: проверьте Active peering, оба маршрута, subnet associations, SG источника и назначения, NACL и локальные Linux firewall rules.
- Permission denied (publickey): проверьте username ec2-user, key pair экземпляра, путь и права PEM. Для nested SSH проверьте `ssh-add -l` локально и доступность forwarding; не печатайте ключ.
- `script` не найден: используйте Mac/Linux/WSL с util-linux/bsd script или запись в клиенте Bitvise.
- После остановки/старта лаборатории проверьте, что реальные адреса и ресурсы не изменились. Остановите/удалите ненужные ресурсы после окончания по правилам Academy; Elastic IP и хранилище могут тарифицироваться отдельно.
