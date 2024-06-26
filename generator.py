from music21 import converter, instrument, stream, note, chord, environment
import numpy as np
from collections import defaultdict
import os

env = environment.Environment()
env['musicxmlPath'] = r'C:\Program Files\MuseScore 4\bin\MuseScore4.exe'


class MCMusicGenerator:
    def __init__(self, training_data):
        self.training_data = training_data
        self.unique_notes = []
        self.cumulative_matrix = None
        self.initial_cumulative = None
        self.process_training_data()

    def process_training_data(self):
        L_i = self.extract_notes_from_midi()
        self.create_transition_matrix(L_i)
        self.calculate_initial_probabilities(L_i)

    def extract_notes_from_midi(self):
        all_sequences = []
        for file_path in self.training_data:
            midi_data = converter.parse(file_path)
            parts = instrument.partitionByInstrument(midi_data)
            if parts:
                notes_to_parse = parts.parts[0].recurse()
            else:
                notes_to_parse = midi_data.flat.notes
            notes_sequence = []
            for element in notes_to_parse:
                if isinstance(element, note.Note):
                    notes_sequence.append(str(element.pitch))
                elif isinstance(element, chord.Chord):
                    notes_sequence.append('.'.join(str(n) for n in element.pitches))
            #notes_sequence.append(notes_sequence[0])
            all_sequences.append(notes_sequence)
        return all_sequences

    def create_transition_matrix(self, sequences):
        note_counts = defaultdict(int)
        for seq in sequences:
            for note in seq:
                note_counts[note] += 1

        self.unique_notes = list(note_counts.keys())
        note_index = {note: i for i, note in enumerate(self.unique_notes)}
        n = len(self.unique_notes)
        transition_matrix = np.zeros((n, n))

        for seq in sequences:
            for i in range(len(seq) - 1):
                curr_note = seq[i]
                next_note = seq[i + 1]
                transition_matrix[note_index[curr_note], note_index[next_note]] += 1

        for i in range(n):
            total = np.sum(transition_matrix[i])
            if total > 0:
                transition_matrix[i] /= total
        self.cumulative_matrix = np.cumsum(transition_matrix, axis=1)

    def calculate_initial_probabilities(self, sequences):
        total_counts = {note: 0 for note in self.unique_notes}
        for seq in sequences:
            for note in seq:
                total_counts[note] += 1

        total_notes = sum(total_counts.values())
        initial_probabilities = np.array([total_counts[note] for note in self.unique_notes])
        initial_probabilities = initial_probabilities / total_notes
        self.initial_cumulative = np.cumsum(initial_probabilities)

    def generate_music(self, num_notes=50):
        first_note_index = np.searchsorted(self.initial_cumulative, np.random.rand())
        music_sequence = [self.unique_notes[first_note_index]]

        current_note_index = first_note_index
        for _ in range(num_notes - 1):
            current_row = self.cumulative_matrix[current_note_index]
            next_note_index = np.searchsorted(current_row, np.random.rand())
            music_sequence.append(self.unique_notes[next_note_index])
            current_note_index = next_note_index

        return music_sequence

    def save_to_midi(self, notes_sequence, file_name="output.mid"):
        midi_stream = stream.Stream()
        for n in notes_sequence:
            if '.' in n:  # it's a chord
                notes_in_chord = n.split('.')
                new_chord = chord.Chord(notes_in_chord)
                midi_stream.append(new_chord)
            else:  # it's a single note
                new_note = note.Note(n)
                midi_stream.append(new_note)
        midi_stream.write('midi', fp=file_name)

    def show_score(self, notes_sequence):
        score_stream = stream.Stream()
        for n in notes_sequence:
            if '.' in n:  # chord
                notes_in_chord = n.split('.')
                new_chord = chord.Chord(notes_in_chord)
                score_stream.append(new_chord)
            else:  # note
                new_note = note.Note(n)
                score_stream.append(new_note)
        score_stream.show()


# Wywołanie
folder_path = 'giantmidi-piano'
files_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(('.mid', '.midi'))]
#print(files_list)

generator = MCMusicGenerator(files_list)
generated_music = generator.generate_music(150)  # Specifying the length of the music piece
generator.save_to_midi(generated_music, "generated_19.mid")
#generator.show_score(generated_music)

folder_path2 = 'ground_truth'
files_list2 = [os.path.join(folder_path2, f) for f in os.listdir(folder_path2) if os.path.isfile(os.path.join(folder_path2, f)) and f.lower().endswith(('.mid', '.midi'))]
#print(files_list)

generator2 = MCMusicGenerator(files_list2)
generated_music = generator2.generate_music(120)  # Specifying the length of the music piece
generator2.save_to_midi(generated_music, "generated_27.mid")
generator.show_score(generated_music)
print(generated_music)

folder_path3 = 'maestro'
files_list3 = [os.path.join(folder_path3, f) for f in os.listdir(folder_path3) if os.path.isfile(os.path.join(folder_path3, f)) and f.lower().endswith(('.mid', '.midi'))]
#print(files_list)

generator3 = MCMusicGenerator(files_list3)
generated_music = generator3.generate_music(100)  # Specifying the length of the music piece
generator3.save_to_midi(generated_music, "generated_25.mid")
generator.show_score(generated_music)

generator4 = MCMusicGenerator(['minuet.mid'])
generated_music = generator4.generate_music(100)  # Specifying the length of the music piece
generator4.save_to_midi(generated_music, "generated_23.mid")

print(generated_music)
