import java.util.Random
import org.apache.log4j.{Level, Logger}
import org.apache.spark.{SparkContext, SparkConf, Partitioner}
import org.apache.spark.storage.StorageLevel

object cpartitioner {
   def main(args:Array[String]){
     //Shield unnecessary log explicitly on the terminal
     Logger.getLogger("org.apache.spark").setLevel(Level.WARN)
     Logger.getLogger("org.eclipse.jetty.server").setLevel(Level.OFF)
     val sparkConf = new SparkConf().setAppName("cpartitioner")
     val sc = new SparkContext(sparkConf)
     val rdd = sc.textFile("/spark/input.txt", 1)
     rdd.cache()
     for (e <- (0 until 10000)) rdd.flatMap(_.split(" ")).map(x => (x,1)).groupByKey(new CustomPartitioner(10000))
     rdd.cache()
     rdd.collect()
   }
}

class CustomPartitioner(numParts:Int) extends Partitioner {
  override def numPartitions: Int = numParts
  override def getPartition(key:Any): Int =  key match{
    case null => 0
    case _ => 1
  }
  override def equals(other:Any):Boolean = other match {
    case cp:CustomPartitioner =>
      cp.numPartitions == numPartitions
    case _ =>
      false
  }
  override def hashCode: Int = numPartitions
}
