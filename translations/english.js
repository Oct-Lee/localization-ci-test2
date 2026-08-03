
const TranslationsCnst = {
  LOADING: "Loading...",
  CONTROLS_DISABLED:
    'Controls are disabled. Please click play to enable controls.',

  COMPUTATIONAL_IMAGING_HEADING: 'Computational Imaging',
  COMPUTATIONAL_IMAGING_MIN: 'Min',
  COMPUTATIONAL_IMAGING_MAX: 'Max',
  THREE_DIMENSION_IMAGING_HEADING: '3D Imaging',
  THREE_DIMENSION_FOVX: 'Horizontal Field of View: ',
  THREE_DIMENSION_FOVY: 'Vertical Field of View: ',
  THREE_DIMENSION_TOP_LEFT_CORNER:
    'Which Ring 1 Channel is Brightest in the Top Left Corner: ',
  COMPUTATIONAL_IMAGING_SUCCESS: 'Computational image saved to %s',
  COMPUTATIONAL_IMAGING_FAILURE: 'Failed to run computational image. %s',
  COMPUTATIONAL_IMAGING_FOLDER_PROMPT: 'Please select a folder',
  COMPUTATIONAL_IMAGING_UNSAVED_SEQUENCE:
    'Please save the changes to the Sequence first',
  COMPUTATIONAL_IMAGING_EMPTY_SEQUENCE:
    'Please include at least 1 Capture in the Sequence',
  COMPUTATIONAL_IMAGING_NO_MODE:
    'Please select at least one mode for computational imaging',
  THREE_DIMENSION_EMPTY_SEQUENCE:
    'Please include at least 3 Captures in the Sequence',
  THREE_DIMENSION_EMPTY_LIGHTING:
    'Every Capture in the Sequence must have a lighting pattern',
  THREE_DIMENSION_MULTIPLE_LIGHTING:
    'Every Capture in the Sequence must have only a single channel active',
  THREE_DIMENSION_DUPLICATE_LIGHTING:
    'Every Capture in the Sequence must be unique',
  IMAGING_SUCCESS: 'Image saved to %s',
  FILE_CAMERA_SUCCESS: 'File Camera saved to %s',
  FILE_CAMERA_FAILURE: 'Failed to run file camera. %s',
  FILE_CAMERA_NOT_SELECT: 'File Camera not select',

  SAVE_IMAGES_TO_FOLDER: 'Save to folder:',
  SAVE_IMAGES: 'Save Images',
  SAVE_FILE_CAMERA: "Save File Camera",
  SAVING_FILE_CAMERA: "Saving File Camera ...",
  FILE_CAMERA_FILE_FORMAT_ALERT: "Please select a valid HDF5 file (.h5 or .hdf5).",
  FILE_CAMERA_FILE_PATH_ALERT: "The filename contains invalid characters and cannot be used for routing. Please rename the file.",
  FILE_CAMERA_SET_IN_USE_FAILURE: "set file camera in use failed: ",
  SAVE_CONFIG: 'Save Config',
  SAVE_NORMALS: 'Save Normals',
  SAVE_HEIGHTS_NORMALIZED: 'Save Heights Normalized',
  SAVE_HEIGHTS_RAW: 'Save Heights Raw',
  SERIAL_PORT: 'serial port',
  HARDWARE_LIGHT_CONFIG: 'Config light of "%s"',
  CONTROLLER: 'light controller',

};

export default TranslationsCnst;
