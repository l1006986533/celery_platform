<template>
  <div class="container">
    <div class="header">
      <h1>🎥 视频目标检测系统</h1>
      <p>上传视频文件，系统将使用YOLO算法进行目标检测和跟踪</p>
    </div>

    <div class="upload-section">
      <el-upload
        class="upload-demo"
        drag
        :action="uploadAction"
        :before-upload="beforeUpload"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :file-list="fileList"
        accept="video/*"
        :disabled="isProcessing"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将视频文件拖拽到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持常见视频格式 (MP4, AVI, MOV等)
          </div>
        </template>
      </el-upload>
    </div>

    <div class="status-section" v-if="taskId || processingStatus">
      <el-card header="处理状态">
        <div class="progress-container" v-if="isProcessing">
          <el-progress :percentage="progressPercentage" :status="progressStatus" />
          <p style="text-align: center; margin-top: 10px;">{{ statusText }}</p>
        </div>

        <div v-if="errorMessage" class="error-message">
          <el-icon><warning /></el-icon>
          {{ errorMessage }}
        </div>

        <div v-if="successMessage" class="success-message">
          <el-icon><success-filled /></el-icon>
          {{ successMessage }}
        </div>
      </el-card>
    </div>

    <div class="video-section" v-if="originalVideo || processedVideo">
      <div class="video-container" v-if="originalVideo">
        <h3>原始视频</h3>
        <video :src="originalVideo" controls></video>
      </div>

      <div class="video-container" v-if="processedVideo">
        <h3>处理后视频</h3>
        <video :src="processedVideo" controls></video>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoProcessor',
  data() {
    return {
      fileList: [],
      taskId: null,
      isProcessing: false,
      processingStatus: null,
      errorMessage: null,
      successMessage: null,
      originalVideo: null,
      processedVideo: null,
      progressPercentage: 0,
      progressStatus: null,
      statusText: '',
      pollInterval: null,
      uploadAction: 'http://localhost:8000/track'
    };
  },
  methods: {
    beforeUpload(file) {
      const isVideo = file.type.startsWith('video/');
      const isLt100M = file.size / 1024 / 1024 < 100;

      if (!isVideo) {
        this.$message.error('请上传视频文件!');
        return false;
      }
      if (!isLt100M) {
        this.$message.error('视频文件大小不能超过100MB!');
        return false;
      }

      this.originalVideo = URL.createObjectURL(file);
      this.errorMessage = null;
      this.successMessage = null;
      this.processedVideo = null;

      return true;
    },

    handleUploadSuccess(response) {
      this.taskId = response.task_id;
      this.isProcessing = true;
      this.progressPercentage = 0;
      this.progressStatus = null;
      this.statusText = '任务已提交，正在处理中...';
      this.startPolling();

      this.$message.success('视频上传成功，开始处理...');
    },

    handleUploadError(err) {
      this.isProcessing = false;
      this.errorMessage = '上传失败: ' + err.message;
      this.$message.error('视频上传失败');
    },

    startPolling() {
      this.pollInterval = setInterval(() => {
        this.checkStatus();
      }, 2000);
    },

    async checkStatus() {
      if (!this.taskId) return;

      try {
        const response = await fetch(`http://localhost:8000/status/${this.taskId}`);
        const data = await response.json();

        this.processingStatus = data.status;

        if (data.status === 'PENDING') {
          this.progressPercentage = Math.min(this.progressPercentage + 10, 90);
          this.statusText = '正在处理视频，请稍候...';
        } else if (data.status === 'SUCCESS') {
          this.progressPercentage = 100;
          this.progressStatus = 'success';
          this.statusText = '处理完成！';
          this.successMessage = '视频处理成功完成！';
          this.processedVideo = `http://localhost:8000${data.output}`;
          this.isProcessing = false;
          this.stopPolling();
          this.$message.success('视频处理完成！');
        } else {
          this.progressStatus = 'exception';
          this.errorMessage = `处理失败: ${data.error}`;
          this.isProcessing = false;
          this.stopPolling();
          this.$message.error('视频处理失败');
        }
      } catch (error) {
        this.errorMessage = `状态检查失败: ${error.message}`;
        this.stopPolling();
      }
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
        this.pollInterval = null;
      }
    }
  },

  beforeUnmount() {
    this.stopPolling();
  }
};
</script>
