# Input Directory

Place dialogue source files here for rendering.

## Content Scope

`Input/` is in-scope project content and is not categorically protected from
review, editing, source control, or release work. See
[`docs/PROJECT_AUTHORITY.md`](../docs/PROJECT_AUTHORITY.md) for the project
owner's scope statement.

## Sample Files

- `Stream_of_Consciousness_Dialogue_2Party_AI_Generated_Test_File.txt` -
  current two-speaker dialogue render input
- `Release_Qualification_5Speaker_Test_File.txt` - five-speaker qualification
  input, derived from the current two-speaker text with utterance text/order
  preserved and speaker labels rotated across five reference voices
- `What_Is_Reality_Output_Test_File.txt` - current monologue render input
- `Recording_Studio_Generic_Teleprompter_File.txt` - recording studio script
- `High_Quality_Seashells_Instruction_set_and_Teleprompter_Text.txt` - voice
  recording instructions and calibration text

## Runtime Subdirectories

`test/` is created on demand by test renders to hold their cache and runtime
artifacts. It, and the other runtime outputs under this directory (`*.pkl`,
`*.json`, `*.diff`, `*.log`, `*.flac`, `*.wav`), are ignored by Git.
