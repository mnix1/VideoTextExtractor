import cv2


def convert_video_to_image_frames(video_path,
                                  on_video_frame_extracted=None,
                                  from_frame=0,
                                  to_frame=None,
                                  frame_increase=1):
    video = cv2.VideoCapture(video_path)
    frames_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    if from_frame >= frames_count:
        raise RuntimeError('start_frame lower than frames_count')
    frame_index = from_frame
    if to_frame is None:
        to_frame = frames_count - 1
    while video.isOpened() and frame_index <= to_frame:
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        successfully_read, frame_data = video.read()
        if not successfully_read:
            raise RuntimeError('Error when reading video frame {}'.format(frame_index))
        # else:
        #     print('Extracted frame {} from {}'.format(frame_index, video_path))
        frame_index = frame_index + frame_increase
        if on_video_frame_extracted is not None:
            on_video_frame_extracted(frame_data, frame_index, video.get(cv2.CAP_PROP_POS_MSEC))
    video.release()
    cv2.destroyAllWindows()
