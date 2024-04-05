# Kontakt Script (KSP) Manual Parser
## Convert KSP PDF Manual to Text Document
- Download the PDF to the `doc_parser/in`folder and rename it to "KSP_Reference_\<major>_\<minor>_Manual_en.pdf"
- The KSP manuals as PDF can be downloaded from
  - v7.8: https://www.native-instruments.com/fileadmin/ni_media/downloads/manuals/kontakt/KSP-7-8-reference-manual-english.pdf
  - v7.6: https://www.native-instruments.com/fileadmin/ni_media/downloads/manuals/kontakt/KSP_Reference_7_6_Manual_en.pdf
  - v7.5: https://www.native-instruments.com/fileadmin/ni_media/downloads/manuals/kontakt/KSP_Reference_Manual_en_7_5_0823.pdf
  - v6.0: https://www.native-instruments.com/fileadmin/ni_media/downloads/manuals/kontakt/KONTAKT_602_KSP_Reference_Manual.pdf
  - v5.7: https://www.native-instruments.com/fileadmin/ni_media/downloads/manuals/KSP_5.7_Reference_Manual_0917.pdf
- The PyPI package [pypdf](https://pypi.org/project/pypdf) is used to extract the text from the PDF file
- Therefore, the method `extract_text(extraction_mode="layout")` is used
- To avoid a ZeroDivion error for the new "layout" mode a special hack was necessary, see `fixed_char_width_hack(a, b)`
  which overwrites the internal `pypdf._text_extraction._layout_mode._fixed_width_page.fixed_char_width`
- The converted file will be stored in `out/ksp_<major>_<minor>/KSP_Reference_Manual.txt.py`
- Note: The \*.py extension for the converted file is necessary to be able within PyCharm to navigate via links directly
  to that line where a certain item is found while parsing. For other file types the navigation by clicking on the link
  would not work. Therefore, in PyCharm after converting a file select the converted file and choose "Override File
  Type" and set it to "Plain text". This will avoid that the syntax check for Python files is done for this file.

## Fix the converted KSP Text Manual
### Preparation
- Copy the converted KSP text manual
  - from `out/ksp_<major>_<minor>/KSP_Reference_Manual.txt.py`
  - to `cfg/ksp_<major>_<minor>/KSP_Reference_Manual_Fixed.txt.py`
- Note: The \*.py extension for the converted file is necessary to be able within PyCharm to navigate via links directly
  to that line where a certain item is found while parsing. For other file types the navigation by clicking on the link
  would not work. Therefore, in PyCharm after converting a file select the converted file and choose "Override File
  Type" and set it to "Plain text". This will avoid that the syntax check for Python files is done for this file.
- In PyCharm select the copied file and select "Override File Type" from the context menu
- In the upcoming dialog choose "Plain Text" to avoid that the file is interpreted as a Python file
- Open `cfg/ksp_<major>_<minor>/KSP_Reference_Manual_Fixed.txt.py`

### Insert Colon for Command Parameters
- In Pycharm for parameters (= `<parameter-name>`) insert a colon and a space (=> `<parameter-name>: `) . Therefore
  - search for the regex:
    ```
    ^(<[a-z-]+>)
    ```
  - and replace it with (there is a space behind the colon!):
    ```
    $1: 
    ```

### Wrapped Command Parameters
- In the PDF there are tables with 2 columns, where inside the cell wrapping is done
- Example:
  ```
  get_target_idx(<group-index>, <mod-index>, <target-name>)
  Returns the modulation target slot index of an internal modulator
  <group-The index of the group (see Index column in Monitor -> Groups pane in
  index>Kontakt).
  <mod-index>The slot index of an internal modulator (LFO, envelope, step modulator...). Can
  be retrieved with get_mod_idx().
  <target-The name of the modulation target slot.
  name>
  ```
- Search for the regex (Note that this contains a newline!):
  ```
  ^(<[a-z-]+-)(.*)
  ^([a-z-]+>)
  ```
 - And replace it with:
   ```
   $1$3: $2
   ```
 
### Wrapped Variable Parameters
- In the PDF there are tables with 2 columns, where inside the cell wrapping is done
- Example:
  ```
  Additional Color and Alpha Parameters
  To be paired with the above control parameters in order to create gradient effects. If not explicitly
  set, they inherit the value of their match from above, resulting in no gradient.
  <<<<<<<<<<<<<<<<<<<< Page 281 >>>>>>>>>>>>>>>>>>>>
  $CONTROL_PAR_WAVE_END_Sets or returns the color for the end of the gradient applied to the
  COLOR waveform (2D) or current waveform (3D).
  $CONTROL_PAR_WAVE_END_Sets or returns the alpha channel (opacity) for the end of the
  ALPHA gradient applied to the waveform (2D) or current waveform (3D).
  $CONTROL_PAR_WAVETABLESets or returns the color for the end of the gradient applied to the
  _END_COLOR background waveforms (3D).
  $CONTROL_PAR_WAVETABLESets or returns the alpha channel (opacity) for the end of the
  _END_ALPHA gradient applied to the background waveforms (3D).
  ```
- There is no easy regex to find such tables
- Best is to search in the original PDF for such tables and note down the page number
- Then in the fixed text KSP manual fix the documentation manually

### Wrapped Parsed Lines
- Sometimes lines are not properly identified, because they are wrapped into the next line
- Example:
  ```
  declare ui_value_edit $<variable-name> (<min>, <max>, <$display-
  ratio>)  
  ```
- To properly parse such lines, remove the newline before the wrapped line

### Wrapped Code Examples
- Example:
  ```
  function SetLabel()
    select ($param_id)
        case $FILT_CUT
            @str := get_engine_par_disp($ENGINE_PAR_CUTOFF, 0, $FILT_SLOT, -1) & "
  Hz"
        case $FILT_RES
            @str := get_engine_par_disp($ENGINE_PAR_RESONANCE, 0, $FILT_SLOT, -1) &
  " %"
        case $OUT_VOL
            @str := get_engine_par_disp($ENGINE_PAR_VOLUME, 0, -1, -1) & " dB"
        case $OUT_PAN
            @str := get_engine_par_disp($ENGINE_PAR_PAN, 0, -1, -1)
    end select
  end function
  ```
- To make the examples better readable, remove the newline before the wrapped line

### Wrapped Pages
- Sometimes documentation is going beyond one page
- Then there might be empty lines or repeated headers to be ignored
- Example:
  ```
  Waveform Property Constants
  To be used with get_ui_wf_property() and set_ui_wf_property().
  <<<<<<<<<<<<<<<<<<<< Page 279 >>>>>>>>>>>>>>>>>>>>
  
  
  
  Waveform Property Constants
  ```
- Delete those lines incl. the repeated header (if any) manually

### Wrapped Variable Comment
- Sometimes variable comments (= text in brackets after a variable) are not properly identified, because they are wrapped into the next line
- Example:
  ```
  
  ```
- To properly parse such lines, remove the newline before the wrapped line

### Indented Constants
- Some constants belong only to a certain variable
- Example:
  ```
  Dirt
  $ENGINE_PAR_DIRT_DRIVEA
  $ENGINE_PAR_DIRT_AMOUNTA
  $ENGINE_PAR_DIRT_BIASA
  $ENGINE_PAR_DIRT_TILTA
  $ENGINE_PAR_DIRT_MODEA
  $NI_DIRT_MODE_I
  $NI_DIRT_MODE_II
  $NI_DIRT_MODE_III
  $ENGINE_PAR_DIRT_SAFETYA
  ```
- Indent such lines with 4 spaces, e.g.
  ```
  Dirt
  $ENGINE_PAR_DIRT_DRIVEA
  $ENGINE_PAR_DIRT_AMOUNTA
  $ENGINE_PAR_DIRT_BIASA
  $ENGINE_PAR_DIRT_TILTA
  $ENGINE_PAR_DIRT_MODEA
      $NI_DIRT_MODE_I
      $NI_DIRT_MODE_II
      $NI_DIRT_MODE_III
  $ENGINE_PAR_DIRT_SAFETYA
  ```
  
## Automatically Parsed Elements
### Page Number in PDF
#### Table of Content Page Number
- Example:
  ```
  <<<<<<<<<<<<<<<<<<<< Table of Contents Page 2 >>>>>>>>>>>>>>>>>>>>
  ```
- It starts with "Table of Contents Page"
- Since after the table of contents start again with 1 it's important to tell the parser how many pages are used for the
  table of contents, see `page_offset` in `BaseMainParser`

#### Normal Content Page Number
- Example:
  ```
  <<<<<<<<<<<<<<<<<<<< Page 321 >>>>>>>>>>>>>>>>>>>>
  ```
- It starts with "Page"

### Table of Contents
- Table of contents is needed to identify the headlines in the scanned chapters

#### Headline
- Example:
  ```
  21. Built-in Variables and Constants      ............................................................................       259
  ```
- A headline starts with a chapter number

#### Category
- Example:
  ```
  General ................................................................................................................                             259
  ```
- Categories are in the table of content, but don't have a chapter number
- Categories are handled only for the chapter they are located

### Callbacks
- Callback start with `on <callback>`

### Widgets
- UI Widgets are used with `declare`

### Commands
- Commands are search starting and ending with a specified chapter

### Variables and Constants
- Variables and Constants are search starting and ending with a specified chapter

#### Normal Variable in Header
- Example:
  ```
  $NI_BUS_OFFSET
  This constant is to be used in the <generic> part of the engine parameter commands to point to
  the instrument bus level. Add the index of the bus you wish to address, e.g. $NI_BUS_OFFSET + 2
  will point to instrument bus 3.
  ```
- The variable is in the first line
- The documentation follows in the next lines

#### Multiple Variables in Header
- Example:
  ```
  $NI_SIGNAL_TIMER_BEAT
  $NI_SIGNAL_TIMER_MS
  $NI_SIGNAL_TRANSP_START
  $NI_SIGNAL_TRANSP_STOP
  These constants can be used with set_listener() or change_listener_par() to set which
  signals will trigger the on listener callback.
  ```
- The variables are in the first lines
- The documentation is valid for all those variables

#### Array in Header
- Example:
  ```
  %GROUPS_SELECTED[<group-idx>]
  Each index of this variable array points to the group with the same index.
  If a group is selected for editing, the corresponding array cell contains a 1, otherwise 0.
  ```
- The parameter of the variable is parsed separately in the square brackets

#### Variable Range in Header
- Example:
  ```
  $MARK_1 ... $MARK_28
  These constants can be used to create a bitmask that is used to group events at will.
  It is intended to be used with by_marks() , set_event_mark(), get_event_mark(),
  delete_event_mark(), mf_set_mark() and mf_get_mark() commands.
  ```
- The documentation is meant for the variables 1 ... n, so the variables in that range must be created

#### Variable Comments
- Example:
  ```
  •  $EVENT_PAR_PLAY_POS (Returns the absolute position of the play cursor within a zone in
  microseconds)
  ```
- Comments for variables are directly after the variable in brackets

#### Table Headline in Header (implemented)
- Example:
  ```
  Path Variables
  $GET_FOLDER_LIBRARY_DIR
  If used with a Kontakt Player encoded NKI: library folder.
  If used with an unencoded NKI: the user content directory.
  $GET_FOLDER_FACTORY_DIR
  The factory folder of Kontakt, mainly used for loading factory IR samples.
  Note: this is not the Kontakt Factory Library folder!
  $GET_FOLDER_PATCH_DIR
  The directory in which the patch was saved.
  If the patch was not saved before, an empty string is returned.
  ```
- The headline is meant for all variables in the table
- The description is variable specific

#### Documentation in Table Header (not implemented yet)
- Example:
  ```
  Time Machine Pro Variables
  User access for the two voice limits (Standard and High Quality) of the Time Machine Pro, to be
  used with set_voice_limit() and get_voice_limit().
  $NI_VL_TMPRO_STANDARD
  $NI_VL_TMRPO_HQ
  ```
- The headline and the following documentation is meant for all the variables in the table

#### Item List (implemented)
- Example:
  ```
  Event Parameter Constants
  Event parameters to be used with set_event_par() and get_event_par():
  •  $EVENT_PAR_0 ... $EVENT_PAR_3
  •  $EVENT_PAR_VOLUME
  •  $EVENT_PAR_PAN
  •  $EVENT_PAR_TUNE
  •  $EVENT_PAR_NOTE
  •  $EVENT_PAR_VELOCITY
  •  $EVENT_PAR_MIDI_CHANNEL
  Event parameters to be used with set_event_par_arr() and get_event_par_arr():
  •  $EVENT_PAR_ALLOW_GROUP
  •  $EVENT_PAR_CUSTOM
  •  $EVENT_PAR_MOD_VALUE_ID
  •  $EVENT_PAR_MOD_VALUE_EX_ID
  Event parameters to be used with get_event_par() only:
  •  $EVENT_PAR_SOURCE (-1 if event originates from outside, otherwise slot number 0 ... 4)
  •  $EVENT_PAR_PLAY_POS (Returns the absolute position of the play cursor within a zone in
  microseconds)
  •  $EVENT_PAR_ZONE_ID (Returns the zone ID of the event- Can only be used with active events.
  Returns -1 if no zone is triggered. Returns the highest zone ID if more than one zone is triggered
  by the event. Make sure the voice is running by writing e.g. wait (1) before retrieving the zone
  ID!)
  Event parameters to be used with set_event_par() and get_event_par() in multi scripts
  only:
  •  $EVENT_PAR_MIDI_COMMAND
  •  $EVENT_PAR_MIDI_BYTE_1
  •  $EVENT_PAR_MIDI_BYTE_2
  Event parameters to be used with mf_set_event_par() and mf_get_event_par():
  •  $EVENT_PAR_POS
  •  $EVENT_PAR_NOTE_LENGTH
  •  $EVENT_PAR_ID
  •  $EVENT_PAR_TRACK_NR
  ```
- Item list headlines end with a colon
- Variables might be prepended with a item symbol ("•")

#### Variable with List of other Constants/Variables (not implemented yet)
- Example 1:
  ```
  $DURATION_QUARTER
  This variable returns the duration of a quarter note in microseconds, with respect to the current
  tempo. Also available:
  $DURATION_EIGHTH
  $DURATION_SIXTEENTH
  $DURATION_QUARTER_TRIPLET
  $DURATION_EIGHTH_TRIPLET
  $DURATION_SIXTEENTH_TRIPLET
  ```
- Example 2:
  ```
  $CONTROL_PAR_TYPE
  Returns the type of the UI widget.
  Only works with get_control_par().
  Possible return values are:
  $NI_CONTROL_TYPE_NONE (UI ID belongs to a normal variable, not a UI widget)
  $NI_CONTROL_TYPE_BUTTON
  $NI_CONTROL_TYPE_KNOB
  $NI_CONTROL_TYPE_MENU
  $NI_CONTROL_TYPE_VALUE_EDIT
  $NI_CONTROL_TYPE_LABEL
  $NI_CONTROL_TYPE_TABLE
  $NI_CONTROL_TYPE_WAVEFORM
  $NI_CONTROL_TYPE_WAVETABLE
  $NI_CONTROL_TYPE_SLIDER
  $NI_CONTROL_TYPE_TEXT_EDIT
  $NI_CONTROL_TYPE_FILE_SELECTOR
  $NI_CONTROL_TYPE_SWITCH
  $NI_CONTROL_TYPE_XY
  $NI_CONTROL_TYPE_LEVEL_METER
  $NI_CONTROL_TYPE_MOUSE_AREA
  $NI_CONTROL_TYPE_PANEL
  ```
- The header contains the main variable
- For the other variables/constants a link to the main variable would be helpful
- The documentation of the main variable should contain also the entire item list

- The constants should have a link to the variable
- Unfortunately, this cannot be distinguished from the Item List

#### Multi-Column Tables (not implemented yet)
- Example 1:
  ```
  $CONTROL_PAR_RECEIVE_DRAG_EVENTS
  Configures whether on ui_control callback of ui_mouse_area gets triggered just for the drop
  event (when set to 0) or also for drag events (when set to 1).
  The UI callback has two built-in variables:
  $NI_MOUSE_EVENT_TYPE Specifies the event type that triggered the callback and can have
  one of the following values:
  $NI_MOUSE_EVENT_TYPE_DND_DROP
  $NI_MOUSE_EVENT_TYPE_DND_DRAG
  $NI_MOUSE_OVER_CONTROL 1: The mouse has entered ui_mouse_area on a drag event
  0: The mouse has left ui_mouse_area on a drag event
  Example
  
  on ui_control ($aMouseArea)
      if ($NI_MOUSE_EVENT_TYPE = $NI_MOUSE_EVENT_TYPE_DROP)
          message(num_elements(!NI_DND_ITEMS_AUDIO))
      end if
  
      if ($NI_MOUSE_EVENT_TYPE = $NI_MOUSE_EVENT_TYPE_DRAG)
          message(num_elements(!NI_DND_ITEMS_AUDIO))
          message($MOUSE_OVER_CONTROL)
      end if
  end on
  ```
- Example 2:
  ```
  Waveform Flag Constants
  To be used with attach_zone(). You can combine flag constants using the bitwise .or..
  $UI_WAVEFORM_USE_SLICEDisplay the zone’s slice markers.
  S
  $UI_WAVEFORM_USE_TABLE Display a per-slice table.
  Note: this only works if the slice markers are also active.
  $UI_WAVEFORM_TABLE_IS_Make the table bipolar.
  BIPOLAR
  $UI_WAVEFORM_USE_MIDI_Display a MIDI drag and drop icon.
  DRAG Note: this only works if the slice markers are also active.
  ```
- Multi-Column tables can't be parsed in a reasonable manner
- Therefore, it's required to manually override those entries and exclude such lines from the parsing
  process

#### Indented Constant List (not implemented yet)
- Example:
  ```
  Source Module
  $ENGINE_PAR_SOURCE_MODE (only works with get_engine_par()!)
      $NI_SOURCE_MODE_SAMPLER
      $NI_SOURCE_MODE_DFD
      $NI_SOURCE_MODE_TONE_MACHINE
      $NI_SOURCE_MODE_TIME_MACHINE_1
      $NI_SOURCE_MODE_TIME_MACHINE_2
      $NI_SOURCE_MODE_TIME_MACHINE_PRO
      $NI_SOURCE_MODE_BEAT_MACHINE
      $NI_SOURCE_MODE_MP60_MACHINE
      $NI_SOURCE_MODE_S1200_MACHINE
      $NI_SOURCE_MODE_WAVETABLE
  $ENGINE_PAR_TRACKING
  $ENGINE_PAR_HQI_MODE
      $NI_HQI_MODE_STANDARD
      $NI_HQI_MODE_HIGH
      $NI_HQI_MODE_PERFECT
  $ENGINE_PAR_SMOOTH
  ...
  ```
- The constants should be linked to the variable
- The documentation of the variable should contain the list of constants

#### Page Wrapped Constant List (not implemented yet)
- Example:
  ```
  $ENGINE_PAR_WT_PHASE_RAND
  $ENGINE_PAR_WT_QUALITY
      $NI_WT_QUALITY_LOFI
      $NI_WT_QUALITY_MEDIUM
      $NI_WT_QUALITY_HIGH
      $NI_WT_QUALITY_BEST
  $ENGINE_PAR_WT_FORM_MODE
      $NI_WT_FORM_LINEAR
      $NI_WT_FORM_SYNC1
      $NI_WT_FORM_SYNC2
      $NI_WT_FORM_SYNC3
      $NI_WT_FORM_SYNC4
  <<<<<<<<<<<<<<<<<<<< Page 286 >>>>>>>>>>>>>>>>>>>>
  
  
  
  Source Module
      $NI_WT_FORM_SYNC5
      $NI_WT_FORM_SYNC6
      $NI_WT_FORM_BENDP
      $NI_WT_FORM_BENDM
      $NI_WT_FORM_BENDMP
      $NI_WT_FORM_BEND2P
      $NI_WT_FORM_BEND2M
      $NI_WT_FORM_BEND2MP
      ...
  $ENGINE_PAR_S1200_FILTER_MODE
      $NI_S1200_FILTER_NONE
      $NI_S1200_FILTER_HIGH
      $NI_S1200_FILTER_HIGH_MID
      $NI_S1200_FILTER_LOW_MID
      $NI_S1200_FILTER_LOW
  ```
  - The constant list shall be merged
  - The repetition of the table header shall be skipped
  - This is done manually in `cfg/ksp<major>_<minor>/KSP_Reference_Manual_Fixed.txt.py`
