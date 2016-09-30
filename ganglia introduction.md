**ganglia介绍**

•	Ganglia是UC Berkeley发起的一个开源集群监视项目，设计用于测量数以千计的节点。Ganglia的核心包含gmond、gmetad以及一个Web前端。主要是用来监控系统性能，如：cpu 、mem、硬盘利用率， I/O负载、网络流量情况等，通过曲线很容易见到每个节点的工作状态，同时可以将历史数据以曲线方式通过php页面呈现。对合理调整、分配系统资源，提高系统整体性能起到重要作用。Ganglia同时具有很好的扩展性，允许用户加入自己所要监控的状态信息。
•	每台计算机都运行一个收集和发送度量数据的名为 gmond 的守护进程。接收所有度量数据的主机可以显示这些数据并且可以将这些数据的精简表单传递到层次结构中。正因为有这种层次结构模式，才使得 Ganglia 可以实现良好的扩展。gmond 带来的系统负载非常少，这使得它成为在集群中各台计算机上运行的一段代码，而不会影响用户性能。所有这些数据多次收集会影响节点性能。网络中的 “抖动”发生在大量小消息同时出现时，可以通过将节点时钟保持一致，来避免这个问题。
•	gmetad可以部署在集群内任一台节点或者通过网络连接到集群的独立主机，它通过单播路由的方式与gmond通信，收集区域内节点的状态信息，并以XML数据的形式，保存在数据库中。
•	由RRDTool工具处理数据，并生成相应的的图形显示，以Web方式直观的提供给客户端。
•	ganglia工作原理
 
图 1  Ganglia整体结构图
Ganglia包括如下几个程序，他们之间通过XDL(xml的压缩格式)或者XML格式传递监控数据，达到监控效果。集群内的节点，通过运行gmond收集发布节点状态信息，然后gmetad周期性的轮询gmond收集到的信息，然后存入rrd数据库，通过web服务器可以对其进行查询展示。
Gmetad 这个程序负责周期性的到各个datasource收集各个cluster的数据，并更新到rrd数据库中。 可以把它理解为服务端。
Gmond 收集本机的监控数据，发送到其他机器上，收集其他机器的监控数据，gmond之间通过udp通信，传递文件格式为xdl。收集的数据供Gmetad读取，默认监听端口8649 ，监听到gmetad请求后发送xml格式的文件。可以把它理解为客户端。
web front-end 一个基于web的监控界面，通常和Gmetad安装在同一个节点上(还需确认是否可以不在一个节点上，因为php的配置文件中ms可配置gmetad的地址及端口)，它从Gmetad取数据，并且读取rrd数据库，生成图片，显示出来。
如上图所示，gmetad周期性的去gmond节点或者gmetad节点poll数据。一个gmetad可以设置多个datasource，每个datasource可以有多个备份，一个失败还可以去其他host取数据。
如果是muticast模式的话，gmond之间还会通过多播来相互传递数据。Gmond本身具有udp send和recv通道，还有一个tcp recv通道。其中udp通道用于向其他gmond节点发送或接受数据，tcp则用来export xml文件，主要接受来自gmetad的请求。Gmetad只有tcp通道，一方面他向datasource发送请求，另一方面会使用一个tcp端口，发布自身收集的xml文件，默认使用8651端口。所以gmetad即可以从gmond也可以从其他的gmetad得到xml数据。
Gmond节点内部模块图如下所示：
 
图 2  Gmond节点模块结构图
如上图所示，主要由三个模块组成，collect and publish模块，该模块周期性的调用一些内部指令获得metric data，然后将这些数据通过udp通道发布给其他gmond节点。Listen Threads，监听其他gmond节点的发送的udp数据，然后将数据存放到内存中。XML export thread负责将数据以xml格式发布出去，比如交给gmetad。
下面重点介绍下unicast模式下ganglia系统内的数据流。
 
图 3  单播状况下集群节点间的数据流
如上图所示，多个gmond节点通过udp向单播的目标host的gmond发送数据，gmetad然后向该目标host的gmond请求xml文件，然后存入rrdtool数据库。 在unicast模式中，图中方框内的组件通常是位于集群内的同一个节点。该节点负责收集存储 显示被监控的各节点的状态信息。
自定义metrics
向ganglia加入自定义metric有两种方法，一种是通过命令行的方式运行gmetric，另一种是通过ganglia提供的面向c和python的扩展模块，加入自定义的模块支持。
配置独立的多播通道
Ganglia系统内置指标
指标名称	单位	描述	类型
load_one	周期内平均	1分钟平均负载	cpu
load_intr	百分比	CPU参与IO中断所占时间百分比	cpu
load_five	周期内平均	5分钟平均负载	cpu
load_sintr	百分比	CPU参与IO软中断所占时间百分比	cpu
load_fifteen	周期内平均	15分钟平均负载	cpu
cpu_idle	百分比	CPU空闲、系统没有显著磁盘IO请求的时间所占百分比	cpu
cpu_aidle	百分比	自启动开始CPU空闲时间所占百分比（不是所有系统都适用）	cpu
cpu_nice	百分比	以user level、nice level运行时的cpu占用率	cpu
cpu_user	百分比	以user level运行时的cpu占用率	cpu
cpu_system	百分比	以system level运行时的cpu占用率	cpu
cpu_wio	百分比	CPU空闲或系统有显著磁盘IO请求的时间所占百分比	cpu
cpu_num	个数	cpu总数（只收集一次）	cpu
cpu_speed	MHz	cpu速率（只收集一次）	cpu
part_max_used	百分比	所有分区已经被占用的百分比	磁盘
disk_total	GB	所有分区总可用磁盘空间	磁盘
disk_free	GB	所有分区总空闲磁盘空间	磁盘
mem_total	KB	总内存空间	内存
proc_run	个数	正在运行的进程数目	内存
mem_cached	KB	缓存（cache）容量	内存
swap_total	KB	swap容量	内存
mem_free	KB	可用内存容量	内存
mem_buffers	KB	buffer容量	内存
mem_shared	KB	shared容量	内存
proc_total	个数	进程总数	内存
swap_free	KB	可用于swap的容量	内存
pkts_out	packets/second	每秒发出的包数	网络
pkts_in	packets/second	每秒接收的包数	网络
bytes_in	bytes/second	每秒受到的字节数	网络
bytes_out	bytes/second	每秒发出的字节数	网络
os_release	字符串	操作系统发布日期	系统
gexec	字符串	gexec可用	系统
mtu	整数	网络最大传输单位	系统
location	字符串	主机位置	系统
os_name	字符串	操作系统名称	系统
boottime	时间	系统最近启动时间	系统
sys_clock	时间	系统时钟时间	系统
heartbeat	整数	上次心跳发送时间	系统
machine_type	字符串	系统架构	系统
 
扩展ganglia监控指标的三种方式及其对比
方式	优势	不足	推荐应用场景
C	执行效率高、占用资源少	开发复杂	需要复杂的操作，或者业务端已经提供了C接口的情况使用
Python	开发简单、快捷、跨平台、比gmetric效率高	性能略低于C模块	没有特殊需求时默认使用pythnon
gmetric	容易实现、便捷
能够避免使用gmond（C语言模块或Python模块）对很少变化的指
标反复轮询	性能低	如果指标很少变化，或者生成指标的应用程序知道指标何时变化场景使用
 
扩展模块示意图
 
 
rrd数据库及rrdtool
•	rrd数据库使用rra文件存储数据，数据库的模型是一个环状结构，每个数据元素为一个时间戳对应的值（值可以有多个，但是多数时候为单个值）。环状存储结构分为多个扇区，每个扇区保存不同取样精度、不容数量的数据。扇区的容量是有限的，当新的数据到来时，会将旧的数据删除（覆盖？）。在每个step指定的取样间隔，会采样一次，存储到入口的扇区，将旧的数据删掉。每N个step（rrdcreate时指定几个）时，会计算一个最旧的N个数据的均值（或者最大、最小、LAST），然后存储在下一阶段的扇区中。
•	rrd意为Round Robin Database。设计理念为按照round-robin的方式进行存储，在一个周期之后（可自己定义），新的数据会覆盖掉原来的数据。所以RRD数据库适合用来存储动态数据，并且不需长期存储。因为是周期性的覆盖旧的数据,所以数据库的大小基本上就会固定下来，并不会随着时间而增大。RRDTOOL是由Tobias Oetiker开发的自由软件，使用RRD作为存储格式。RRDTOOL提供了很多工具用来对RRD数据库进行操作，包括创建，更新，查询，以及生成显示图等。RRDTOOL同时也提供了很多语言的API以方便操作。
•	Ganglia是一个分布式的监控系统，采用RRD数据库进行数据存储和可视化。Hadoop源码包里即有一个与ganglia相关的配置文件，修改一些参数和对ganglia进行一些设置即可对hadoop集群进行监控。每个不同的属性的数据都存在一个RRD数据库里。
•	RRD数据库的结构与其他的线性结构数据库不同，其他数据库都是以栏或其他参数来定义表格的，这种定义有时候会非常复杂，尤其数据库比较大时。RRDtool数据库主要用于监测，因此结构非常简单，需要被定义的参数是那些拥有值的变量以及这些值的档案。由于与时间关系密切，这里还定义了一些与时间相关的参数。鉴于这种结构，RRDtool数据库的定义还提供了在缺乏更新数据的情况下应采取的特定动作。与RRDtool 数据库相关的一些术语包括：Data Source (DS), heartbeat, Date Source Type (DST), Round Robin Archive (RRA), 以及Consolidation Function (CF)等。 
