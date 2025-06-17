import librosa
import numpy as np
import soundfile as sf
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTE_TO_SOLFEGE = {
    'C': 'Do',
    'C#': 'Do#',
    'D': 'Re',
    'D#': 'Re#',
    'E': 'Mi',
    'F': 'Fa',
    'F#': 'Fa#',
    'G': 'Sol',
    'G#': 'Sol#',
    'A': 'La',
    'A#': 'La#',
    'B': 'Si'
}

def note_index_to_solfege(index):
    note = NOTE_NAMES[index % 12]
    octave = 4 + (index // 12)
    sol = NOTE_TO_SOLFEGE[note]

    # Mark octave with apostrophes: Do Do' Do'' etc.
    if octave < 4:
        sol = sol.lower()  # optional: lowercase for low octave
    elif octave == 4:
        pass  # normal Do
    else:
        sol += "'" * (octave - 4)  # Do' Do'' ...

    return sol

def analyze_notes_solfege(audio_path, quang_interval=0):
    y, sr = librosa.load(audio_path)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

    solfege_seq = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        freq = pitches[index, t]
        if freq > 0:
            _, note_idx = freq_to_note(freq)
            note_idx += quang_interval
            sol = note_index_to_solfege(note_idx)
            solfege_seq.append(sol)
    return solfege_seq

def freq_to_note(freq):
    if freq == 0:
        return "Rest"
    A4 = 440.0
    semitones = 12 * np.log2(freq / A4)
    note_index = int(round(semitones)) + 9  # A4 is the 9th note
    octave = 4 + (note_index // 12)
    note = NOTE_NAMES[note_index % 12]
    return f"{note}{octave}", note_index

def note_index_to_name(index):
    note = NOTE_NAMES[index % 12]
    octave = 4 + (index // 12)
    return f"{note}{octave}"

def analyze_notes_with_interval(audio_path, quang_interval=3):
    y, sr = librosa.load(audio_path)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

    transformed_notes = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        freq = pitches[index, t]
        if freq > 0:
            note, note_idx = freq_to_note(freq)
            new_idx = note_idx + quang_interval  # Increase by 'quãng'
            new_note = note_index_to_name(new_idx)
            transformed_notes.append(new_note)
    return transformed_notes

notes = analyze_notes_with_interval("demo.mp3", quang_interval=4)  # +4 semitones (a major third)
print(notes)

