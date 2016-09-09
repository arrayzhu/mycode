import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import java.io.IOException;
import java.lang.String;
import java.util.ArrayList;
import java.util.List;

public class FindFileOnHDFS {
    public static String[] getFileList(String path)
            throws IOException {
        Configuration conf = new Configuration();
        conf.addResource(new Path("/home/hadoop/hadoop-2.6.0/etc/hadoop/core-site.xml"));
        conf.addResource(new Path("/home/hadoop/hadoop-2.6.0/etc/hadoop/hdfs-site.xml"));
        //conf.addResource("/home/hadoop/hadoop-2.6.0/etc/hadoop/core-site.xml");
        FileSystem fs = FileSystem.get(conf);
        System.out.println(fs.getHomeDirectory());
        List<String> files = new ArrayList<String>();
        Path s_path = new Path(path);
        if(fs.exists(s_path))
        {
            for(FileStatus status:fs.listStatus(s_path)) {
                System.out.println(status.getPath());
                files.add(status.getPath().toString());
            }
        }
        fs.close();
        return files.toArray(new String[]{});
    }

    public static String res = null;

    /**
     * 得到一个目录(不包括子目录)下的所有名字匹配上pattern的文件名
     * @param fs
     * @param folderPath
     * @param pattern 用于匹配文件名的正则
     * @return
     * @throws IOException
     */
    public static void getFilesUnderFolder(FileSystem fs, Path folderPath, String pattern) throws IOException {
        if (fs.exists(folderPath)) {
            String tmp = null;
            FileStatus[] fileStatus = fs.listStatus(folderPath);
            for (int i = 0; i < fileStatus.length; i++) {
                FileStatus fileStatu = fileStatus[i];
                // 如果是目录，递归向下找
                if (!fileStatu.isDirectory()) {
                    Path path = fileStatu.getPath();
                    if (path.getName().contains(pattern)) {
                        res = path.toString();
                        return;
                    }
                } else {
                    getFilesUnderFolder(fs, fileStatu.getPath(), pattern);
                }
            }
        }
    }

    public static void main(String[] args)
            throws IOException {
        String uri = "hdfs://Spark-Master:9000/";
        Path path = new Path(uri);
        Configuration conf = new Configuration();
        conf.addResource(new Path("/home/hadoop/hadoop-2.6.0/etc/hadoop/core-site.xml"));
        conf.addResource(new Path("/home/hadoop/hadoop-2.6.0/etc/hadoop/hdfs-site.xml"));
        FileSystem fs = FileSystem.get(conf);
        //System.out.println(fs.getHomeDirectory());

        getFilesUnderFolder(fs, path, "jar");
        System.out.println(res);

    }
}
