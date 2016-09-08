package org.apache.spark.memory

import scala.collection.mutable

import org.apache.spark.SparkConf
import org.apache.spark.storage.{BlockStatus, BlockId}

//设置参数spark.unifiedMemory.useStaticStorageRegion。修改maxStorageMemory函数，该值会影响在Job UI上显示的最大内存
override def maxStorageMemory: Long = synchronized {
  if(useStaticStorageMemory){
  storageRegionSize
}else{
  maxMemory - onHeapExecutionMemoryPool.memoryUsed
}
}

//修改acquireStorageMemory函数，增加以下的代码，修改maxBorrowMemory的值
if(useStaticStorageMemory&&(storageRegionSize-storageMemoryPool.poolSize) < onHeapExecutionMemoryPool.memoryFree){
  maxBorrowMemory = storageRegionSize - storageMemoryPool.poolSize
}


