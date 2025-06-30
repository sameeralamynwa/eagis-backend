import EditorJS from "@editorjs/editorjs";
import CodeTool from "@editorjs/code";
import Header from "@editorjs/header";
import EditorjsList from "@editorjs/list";
import SimpleImage from "@editorjs/simple-image";
import Quote from "@editorjs/quote";
import Marker from "@editorjs/marker";
import Table from "@editorjs/table";

window.createEditorJs = function createEditorJs(elementId) {
  const inputElement = document.getElementById(elementId);
  if (!inputElement) {
    throw Error(
      `Please add a input with id "${elementId}" in order for editor js to work`,
    );
  }

  const editor = new EditorJS({
    holder: `${elementId}-json`,
    tools: {
      header: {
        class: Header,
        inlineToolbar: ["marker", "link"],
        config: {
          placeholder: "Header",
        },
        shortcut: "CMD+SHIFT+H",
      },
      image: {
        class: SimpleImage,
        inlineToolbar: true,
      },
      list: {
        class: EditorjsList,
        inlineToolbar: true,
        config: {
          defaultStyle: "unordered",
        },
      },
      quote: {
        class: Quote,
        inlineToolbar: true,
        config: {
          quotePlaceholder: "Enter a quote",
          captionPlaceholder: "Quote's author",
        },
        shortcut: "CMD+SHIFT+O",
      },
      marker: {
        class: Marker,
        shortcut: "CMD+SHIFT+M",
      },
      table: {
        class: Table,
        inlineToolbar: true,
        shortcut: "CMD+ALT+T",
      },
      code: CodeTool,
    },

    onChange: () => {
      editor
        .save()
        .then((outputData) => {
          inputElement.value = JSON.stringify(outputData);
        })
        .catch((error) => {
          console.error("Saving failed: ", error);
        });
    },
  });
};
