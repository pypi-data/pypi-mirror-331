from django.forms.widgets import Textarea
from django.utils.safestring import mark_safe

class PersianEditorWidget(Textarea):
    class Media:
        js = ('persian_editor/js/editor.js',)
        css = {
            'all': ('persian_editor/css/editor.css',)
        }

    def render(self, name, value, attrs=None, renderer=None):
        textarea_html = super().render(name, value, attrs, renderer)
        element_id = attrs.get('id')
        html = f'''
            <div class="persian-editor-container" id="{element_id}_container">
                <div id="{element_id}_toolbar" class="editor-toolbar">
                    <button type="button" title="Undo" onclick="execCommand('{element_id}', 'undo')">↺</button>
                    <button type="button" title="Redo" onclick="execCommand('{element_id}', 'redo')">↻</button>
                    <button type="button" title="Bold" onclick="execCommand('{element_id}', 'bold')"><b>B</b></button>
                    <button type="button" title="Italic" onclick="execCommand('{element_id}', 'italic')"><i>I</i></button>
                    <button type="button" title="Underline" onclick="execCommand('{element_id}', 'underline')"><u>U</u></button>
                    <button type="button" title="Strike" onclick="execCommand('{element_id}', 'strikeThrough')"><s>S</s></button>
                    <button type="button" title="Align Left" onclick="execCommand('{element_id}', 'justifyLeft')">⇤</button>
                    <button type="button" title="Align Center" onclick="execCommand('{element_id}', 'justifyCenter')">≡</button>
                    <button type="button" title="Align Right" onclick="execCommand('{element_id}', 'justifyRight')">⇥</button>
                    <button type="button" title="Justify" onclick="execCommand('{element_id}', 'justifyFull')">☰</button>
                    <button type="button" title="Ordered List" onclick="execCommand('{element_id}', 'insertOrderedList')">1.</button>
                    <button type="button" title="Unordered List" onclick="execCommand('{element_id}', 'insertUnorderedList')">•</button>
                    <button type="button" title="Insert Link" onclick="triggerLinkPrompt('{element_id}')">🔗</button>
                    <button type="button" title="Insert Image" onclick="triggerImageUpload('{element_id}')">🖼</button>
                    <button type="button" title="Toggle HTML" onclick="toggleSourceView('{element_id}')">HTML</button>
                    <button type="button" title="Clear Formatting" onclick="clearFormatting('{element_id}')">✖</button>
                    <button type="button" title="Fullscreen" onclick="toggleFullscreen('{element_id}')">⛶</button>
                    <input type="color" id="{element_id}_text_color" onchange="execCommandValue('{element_id}', 'foreColor', this.value)" title="Text Color">
                    <input type="color" id="{element_id}_bg_color" onchange="execCommandValue('{element_id}', 'hiliteColor', this.value)" title="Background Color">
                </div>
                <div id="{element_id}_editor" class="editor-content" contenteditable="true" dir="rtl" data-source-view="false">
                    {value or ''}
                </div>
                <input type="file" id="{element_id}_image_input" style="display: none;" accept="image/*">
            </div>
            {textarea_html}
            <script type="text/javascript">
                document.addEventListener("DOMContentLoaded", function() {{
                    initPersianEditor("{element_id}");
                }});
            </script>
        '''
        return mark_safe(html)
