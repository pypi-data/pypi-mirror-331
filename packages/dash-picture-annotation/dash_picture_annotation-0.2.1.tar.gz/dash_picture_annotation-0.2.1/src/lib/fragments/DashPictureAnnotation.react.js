import React, {useState, useEffect, useRef} from "react";
import {useMeasure} from "react-use";
import {useImageSize} from "react-image-size";
import {useLRUCache} from "use-lru-cache";
import clsx from "clsx";
import {type, isNil, isEmpty} from "ramda";
import disableScroll from "disable-scroll";

import {
  sanitizeDataFast,
  sanitizeOptions,
  sanitizeScale,
  requireMin,
} from "../utils";
import {getBoxColor, getGlobalBoxColor} from "../colorhash";

import {ReactPictureAnnotation} from "react-picture-annotation";
import Dropdown from "./Dropdown.react";
import Input from "./Input.react";
import OcticonFileMedia24 from "../icons/filemedia";
import OcticonLock24 from "../icons/lock";

import {
  propTypes,
  defaultProps,
} from "../components/DashPictureAnnotation.react";
import styles from "./DashPictureAnnotation.module.css";

/**
 * Get the default value of style annotation.
 *
 * This value in needed only when the `style_annotation` property is specified.
 *
 * @returns {Object.<string, (number|string)>} - CSS styles used by annotation items.
 */
const default_style_annotation = () => ({
  /** text area **/
  padding: 5, // text padding
  fontSize: 12, // text font size
  fontColor: "#212529", // text font color
  fontBackground: "#f8f9fa", // text background color
  fontFamily:
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', Helvetica, Arial, sans-serif",

  /** stroke style **/
  lineWidth: 2, // stroke width
  shapeBackground: "hsla(210, 16%, 93%, 0.2)", // background color in the middle of the marker
  shapeStrokeStyle: "#f8f9fa", // shape stroke color
  shadowBlur: 10, // stroke shadow blur
  shapeShadowStyle: "hsla(210, 9%, 31%, 0.35)", // shape shadow color

  /** transformer style **/
  transformerBackground: "#5c7cfa",
  transformerSize: 10,
});

/**
 * Wait until the property of an object is available.
 * @param {object} obj - The object containing the property.
 * @param {object} prop - The name of the property to be accessed.
 * @param {object} interval - The waiting interval. The unit is ms.
 * @returns {Promise<any>} A promise returning the property of `obj`.
 */
const waitForProperty = (obj, prop, interval = 100) => {
  return new Promise((resolve, reject) => {
    const checkProperty = () => {
      if (obj[prop] !== undefined) {
        resolve(obj[prop]);
      } else {
        setTimeout(checkProperty, interval);
      }
    };
    checkProperty();
  });
};

/**
 * DashPictureAnnotation is a Dash porting version for the React component:
 * `react-picture-annotation/ReactPictureAnnotation`
 *
 * This component provides a annotator that allows users to create, modify, or delete
 * the annotation information for a specific picture. This dash version has been
 * upgraded by adding the following features:
 * 1. Responsive size with respect to the parent component.
 * 2. Annotation type specified by a selector rather than an input box.
 * 3. Only trigger the data update when the mouse is released.
 */
const DashPictureAnnotation = (props) => {
  const {
    id,
    class_name,
    style,
    style_annotation,
    colors,
    image,
    data,
    options,
    selected_id,
    placeholder_input,
    placeholder_dropdown,
    clearable_dropdown,
    disabled,
    is_color_dynamic,
    size_minimal,
    init_scale,
    loading_state,
    setProps,
  } = props;

  const [initWidth, setInitWidth] = useState(undefined);
  const [prevWidth, setPrevWidth] = useState(0);
  const [curTimeStamp, setCurTimeStamp] = useState(Date.now());
  const [frequentData, setFrequentData] = useState(sanitizeDataFast(data).data);

  const [ref, {x, y, width, height, top, right, bottom, left}] = useMeasure();
  const [dimensions, {loading, error}] = useImageSize(image);

  const lruCacheHash = useLRUCache(30);
  const lruCacheName = useLRUCache(30);

  const widthMin = requireMin(
    type(size_minimal) == "Number" ? size_minimal : size_minimal?.width
  );
  const heightMin = requireMin(
    type(size_minimal) == "Number" ? size_minimal : size_minimal?.height
  );

  const sanitizeFrequentData = (newData) => {
    if (type(newData) == "Array") {
      const sanitizedNewData = newData.filter((element) => {
        let mark = element.mark;
        if (mark) {
          return (
            Math.abs(mark.width) > widthMin && Math.abs(mark.height > heightMin)
          );
        } else {
          return false;
        }
      });
      return sanitizedNewData;
    }
    return [];
  };

  const onSelect = (selectedId) => {
    setProps({selected_id: selectedId});
  };

  const onChange = (newData) => {
    setFrequentData(newData);
  };

  const handleMouseUp = () => {
    setProps({
      data: {
        timestamp: Date.now(),
        data: sanitizeFrequentData(frequentData),
      },
    });
  };

  /**
   * Reset the colors of the shape.
   *
   * This method will be called when any comment of the frequentData is reset by users.
   * Using this method will cause the color of each box reset.
   *
   * @param {ReactPictureAnnotation} anno - The ref object to the annotator. Note that
   *   this value will not be checked by this method.
   */
  const resetShapeColors = (anno) => {
    anno.shapes = anno.shapes.map((shape) => {
      if (is_color_dynamic || colors) {
        shape.shapeStyle = Object.assign(
          {},
          anno.annotationStyle,
          getBoxColor(
            shape,
            colors,
            lruCacheHash,
            lruCacheName,
            is_color_dynamic
          )
        );
      } else {
        shape.shapeStyle = anno.annotationStyle;
      }
      return shape;
    });
    anno.onShapeChange();
  };

  const getStyleAnnotation = (styleAnnotation) => {
    if (type(styleAnnotation) === "Object") {
      return Object.assign({}, default_style_annotation(), styleAnnotation);
    } else if (type(styleAnnotation) === "String") {
      return Object.assign(
        {},
        default_style_annotation(),
        getGlobalBoxColor(styleAnnotation, lruCacheName)
      );
    } else {
      return undefined;
    }
  };

  const getModifiedOnDelete = (onDelete) => {
    return () => {
      const waitOnDelete = new Promise((resolve) => {
        onDelete();
        resolve();
      });
      waitOnDelete.then(() => {
        const anno = ref_anno.current;
        if (anno.props?.annotationData) {
          setProps({
            data: {
              timestamp: Date.now(),
              data: sanitizeFrequentData(anno.props.annotationData),
            },
          });
          setFrequentData(anno.props.annotationData);
        }
        return;
      });
    };
  };

  const sanitizedOptions = sanitizeOptions(options);

  const selector =
    sanitizedOptions && sanitizedOptions.length
      ? (value, onChange, onDelete) => (
          <Dropdown
            value={value}
            onChange={onChange}
            onDelete={getModifiedOnDelete(onDelete)}
            options={sanitizedOptions}
            placeholder={placeholder_dropdown || placeholder_input || ""}
            isClearable={clearable_dropdown}
          />
        )
      : (value, onChange, onDelete) => {
          return (
            <Input
              value={value}
              onChange={onChange}
              onDelete={getModifiedOnDelete(onDelete)}
              options={sanitizedOptions}
              placeholder={placeholder_input || ""}
            />
          );
        };

  useEffect(() => {
    const _data = sanitizeDataFast(data);
    const timestamp = _data.timestamp;
    if (!frequentData.timestamp || timestamp > frequentData.timestamp) {
      setFrequentData(sanitizeFrequentData(_data.data));
    }
    setCurTimeStamp(timestamp);
  }, [data]);

  useEffect(() => {
    setCurTimeStamp(Date.now());
  }, [style_annotation, is_color_dynamic, colors, image, disabled]);

  useEffect(() => {
    const anno = ref_anno.current;
    if (anno) {
      resetShapeColors(anno);
    }
  }, [curTimeStamp]);

  var ref_anno = useRef();

  const configureInitScale = (anno, scale, targetFullWidth, imgSize) => {
    const normScale = (scale.scale * targetFullWidth) / imgSize.width;
    anno.scaleState.scale = normScale;
    anno.scaleState.originX = scale.offset_x * (width - normScale * imgSize.width);
    anno.scaleState.originY = scale.offset_y * (height - normScale * imgSize.height);
    anno.setState({imageScale: anno.scaleState});
    anno.onImageChange();
    anno.onShapeChange();
  };

  useEffect(() => {
    const anno = ref_anno.current;
    if (anno && dimensions && type(initWidth) != "Undefined") {
      const initScaleOptions = sanitizeScale(init_scale);
      waitForProperty(anno, "currentImageElement")
        .then((value) => {
          configureInitScale(
            anno,
            initScaleOptions,
            width > 0
              ? Math.min(
                  width,
                  dimensions
                    ? (dimensions.width * height) / dimensions.height
                    : width
                )
              : initWidth,
            dimensions
          );
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
    // if (anno && type(init_scale) === "Number") {
    //   anno.onImageChange();
    //   anno.onShapeChange();
    // }
    return () => {};
  }, [init_scale]);

  useEffect(() => {
    const anno = ref_anno.current;
    if (anno && dimensions && !initWidth && Math.abs(width) > 1e-3) {
      const newInitWidth = Math.min(
        width,
        (dimensions.width * height) / dimensions.height
      );
      setInitWidth(newInitWidth);
      const initScaleOptions = sanitizeScale(init_scale);
      waitForProperty(anno, "currentImageElement")
        .then((value) => {
          configureInitScale(anno, initScaleOptions, newInitWidth, dimensions);
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
    if (width != prevWidth) {
      if (prevWidth > 0) {
        let NeedsUpdate = dimensions
          ? width / dimensions.width < height / dimensions.height
          : true;
        let ratio = width / prevWidth;
        let decsize = (width - prevWidth) / 2;
        if (anno) {
          if (NeedsUpdate) {
            anno.scaleState.scale = anno.scaleState.scale * ratio;
          }
          const {originX, originY} = anno.scaleState;
          if (NeedsUpdate) {
            const offsetX = 0;
            const offsetY = height / 2;
            anno.scaleState.originX = offsetX - (offsetX - originX) * ratio;
            anno.scaleState.originY = offsetY - (offsetY - originY) * ratio;
          } else {
            anno.scaleState.originX = originX + decsize;
          }
          anno.setState({imageScale: anno.scaleState});
        }
      }
      setPrevWidth(width);
    }
    return () => {};
  }, [init_scale, width]);

  useEffect(() => {
    const anno = ref_anno.current;
    if (anno) {
      anno.onImageChange();
      anno.onShapeChange();
    }
  }, [prevWidth]);

  if (isNil(image) || isEmpty(image)) {
    return (
      <div
        id={id}
        ref={ref}
        className={clsx(
          styles["annotation-container"],
          styles.disabled,
          class_name
        )}
        style={style}
        data-dash-is-loading={
          (loading_state && loading_state.is_loading) || undefined
        }
      >
        <div className={styles["overlay-container"]}>
          <div className={styles["overlay-inner-container"]}>
            <div className={styles["icon-container"]}>
              <OcticonFileMedia24 className={styles.icon} />
              <p className={styles.text}>Needs an image to annotate.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading || error) {
    <div
      id={id}
      ref={ref}
      className={clsx(
        styles["annotation-container"],
        styles.disabled,
        class_name
      )}
      style={style}
      data-dash-is-loading={
        (loading_state && loading_state.is_loading) || undefined
      }
    >
      <div className={styles["overlay-container"]}>
        <div className={styles["overlay-inner-container"]}>
          <div className={styles["icon-container"]}>
            <OcticonFileMedia24 className={styles.icon} />
            <p className={styles.text}>Image not loaded.</p>
          </div>
        </div>
      </div>
    </div>;
  }

  if (disabled) {
    return (
      <div
        id={id}
        ref={ref}
        className={clsx(
          styles["annotation-container"],
          styles.disabled,
          class_name
        )}
        style={style}
        data-dash-is-loading={
          (loading_state && loading_state.is_loading) || undefined
        }
      >
        <div className={styles["overlay-container"]}>
          <div className={styles["overlay-inner-container"]}>
            <div className={styles["icon-container"]}>
              <OcticonLock24 className={styles.icon} />
              <p className={styles.text}>Disabled.</p>
            </div>
          </div>
        </div>
        <img
          src={image}
          width={width}
          height={height}
          title={"Disabled annotator"}
        />
      </div>
    );
  }

  return (
    <div
      id={id}
      ref={ref}
      className={clsx(styles["annotation-container"], class_name)}
      style={style}
      data-dash-is-loading={
        (loading_state && loading_state.is_loading) || undefined
      }
      onMouseUp={handleMouseUp}
      onMouseEnter={(e) => {
        disableScroll.on();
      }}
      onMouseLeave={(e) => {
        disableScroll.off();
      }}
    >
      <ReactPictureAnnotation
        ref={ref_anno}
        image={image}
        onSelect={onSelect}
        onChange={onChange}
        inputElement={selector}
        annotationData={frequentData}
        annotationStyle={getStyleAnnotation(style_annotation)}
        width={width}
        height={height}
      />
    </div>
  );
};

DashPictureAnnotation.defaultProps = defaultProps;

DashPictureAnnotation.propTypes = propTypes;

export default DashPictureAnnotation;
