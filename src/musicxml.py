import xml.etree.ElementTree as ET
from xml.dom import minidom

from src.data_classes import Note, Measure, Part, Score


class MusicXML:
    """Read and write MusicXML files."""

    @staticmethod
    def read(filepath: str) -> Score:
        """Parse a MusicXML file and return a Score object."""
        tree = ET.parse(filepath)
        root = tree.getroot()

        score = Score()

        # Parse metadata
        work = root.find("work")
        if work is not None:
            work_title = work.find("work-title")
            if work_title is not None:
                score.title = work_title.text

        # Parse credits for title, subtitle, and composer
        for credit in root.findall("credit"):
            credit_type_elem = credit.find("credit-type")
            credit_words_elem = credit.find("credit-words")

            if credit_type_elem is not None and credit_words_elem is not None:
                credit_type = credit_type_elem.text
                credit_text = credit_words_elem.text

                if credit_type == "title":
                    score.title = credit_text
                elif credit_type == "subtitle":
                    score.subtitle = credit_text
                elif credit_type == "composer":
                    score.composer = credit_text

        # Get part list to find part names
        part_names = {}
        part_list = root.find("part-list")
        if part_list is not None:
            for score_part in part_list.findall("score-part"):
                part_id = score_part.get("id")
                part_name_elem = score_part.find("part-name")
                if part_name_elem is not None:
                    part_names[part_id] = part_name_elem.text

        # Parse all parts
        for part_elem in root.findall("part"):
            part_id = part_elem.get("id")
            if not part_id:
                continue
            part = Part(part_id=part_id, name=part_names.get(part_id))

            # Parse all measures
            for measure_elem in part_elem.findall("measure"):
                measure_number_str = measure_elem.get("number")
                if not measure_number_str:
                    continue
                measure_number = int(measure_number_str)
                measure_width = measure_elem.get("width")
                measure = Measure(
                    number=measure_number,
                    width=float(measure_width) if measure_width else None
                )

                # Parse all notes in the measure
                for note_elem in measure_elem.findall("note"):
                    note = MusicXML._parse_note(note_elem)
                    measure.add_note(note)

                part.add_measure(measure)

            score.add_part(part)

        return score

    @staticmethod
    def _parse_note(note_elem: ET.Element) -> Note:
        """Parse a note element into a Note object."""
        # Check if it's a rest
        is_rest = note_elem.find("rest") is not None

        # Get pitch information
        step = None
        octave = None
        if not is_rest:
            pitch_elem = note_elem.find("pitch")
            if pitch_elem is not None:
                step_elem = pitch_elem.find("step")
                octave_elem = pitch_elem.find("octave")
                if step_elem is not None and step_elem.text:
                    step = step_elem.text
                if octave_elem is not None and octave_elem.text:
                    octave = int(octave_elem.text)

        # Get duration
        duration = 0
        duration_elem = note_elem.find("duration")
        if duration_elem is not None and duration_elem.text:
            duration = int(duration_elem.text)

        # Get note type (quarter, half, etc.)
        note_type = None
        type_elem = note_elem.find("type")
        if type_elem is not None:
            note_type = type_elem.text

        # Get voice
        voice = None
        voice_elem = note_elem.find("voice")
        if voice_elem is not None:
            voice = voice_elem.text

        # Get staff
        staff = None
        staff_elem = note_elem.find("staff")
        if staff_elem is not None and staff_elem.text:
            staff = int(staff_elem.text)

        # Get stem
        stem = None
        stem_elem = note_elem.find("stem")
        if stem_elem is not None:
            stem = stem_elem.text

        # Get position
        default_x = note_elem.get("default-x")
        default_y = note_elem.get("default-y")

        return Note(
            step=step,
            octave=octave,
            duration=duration,
            note_type=note_type,
            voice=voice,
            staff=staff,
            is_rest=is_rest,
            stem=stem,
            default_x=float(default_x) if default_x else None,
            default_y=float(default_y) if default_y else None
        )

    @staticmethod
    def write(score: Score, filepath: str) -> None:
        """Write a Score object to a MusicXML file."""
        # Create root element
        root = ET.Element("score-partwise", version="4.0")

        # Add work element
        if score.title:
            work = ET.SubElement(root, "work")
            work_title = ET.SubElement(work, "work-title")
            work_title.text = score.title

        # Add identification
        identification = ET.SubElement(root, "identification")
        if score.composer:
            creator = ET.SubElement(identification, "creator", type="composer")
            creator.text = score.composer

        # Add part-list
        part_list = ET.SubElement(root, "part-list")
        for part in score.parts:
            score_part = ET.SubElement(part_list, "score-part", id=part.part_id)
            part_name = ET.SubElement(score_part, "part-name")
            part_name.text = part.name or "Music"

        # Add parts
        for part in score.parts:
            part_elem = ET.SubElement(root, "part", id=part.part_id)

            for measure in part.measures:
                measure_elem = ET.SubElement(part_elem, "measure", number=str(measure.number))

                # Add attributes to first measure
                if measure.number == 1:
                    attributes = ET.SubElement(measure_elem, "attributes")
                    divisions = ET.SubElement(attributes, "divisions")
                    divisions.text = "2"  # 2 divisions per quarter note

                    key = ET.SubElement(attributes, "key")
                    fifths = ET.SubElement(key, "fifths")
                    fifths.text = "0"

                    time = ET.SubElement(attributes, "time")
                    beats = ET.SubElement(time, "beats")
                    beats.text = "4"
                    beat_type = ET.SubElement(time, "beat-type")
                    beat_type.text = "4"

                    clef = ET.SubElement(attributes, "clef")
                    sign = ET.SubElement(clef, "sign")
                    sign.text = "G"
                    line = ET.SubElement(clef, "line")
                    line.text = "2"

                    # Add tempo directive to first measure
                    if score.tempo:
                        direction = ET.SubElement(measure_elem, "direction", placement="above")
                        direction_type = ET.SubElement(direction, "direction-type")
                        metronome = ET.SubElement(direction_type, "metronome", parentheses="no")
                        beat_unit = ET.SubElement(metronome, "beat-unit")
                        beat_unit.text = "quarter"
                        per_minute = ET.SubElement(metronome, "per-minute")
                        per_minute.text = str(score.tempo)
                        sound = ET.SubElement(direction, "sound")
                        sound.set("tempo", str(score.tempo))

                # Add notes
                for note in measure.notes:
                    MusicXML._write_note(measure_elem, note)

        # Create tree and write to file with pretty formatting
        xml_str = ET.tostring(root, encoding='unicode')

        # Pretty print
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")

        # Remove extra blank lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    @staticmethod
    def _write_note(measure_elem: ET.Element, note: Note) -> None:
        """Write a Note object to XML."""
        note_elem = ET.SubElement(measure_elem, "note")

        if note.is_rest:
            ET.SubElement(note_elem, "rest")
        else:
            # Add pitch
            pitch = ET.SubElement(note_elem, "pitch")
            step = ET.SubElement(pitch, "step")
            step.text = note.step
            octave = ET.SubElement(pitch, "octave")
            octave.text = str(note.octave)

        # Add duration
        duration = ET.SubElement(note_elem, "duration")
        duration.text = str(note.duration)

        # Add type
        if note.note_type:
            type_elem = ET.SubElement(note_elem, "type")
            type_elem.text = note.note_type

        # Add dot for dotted notes (duration that's 1.5x the base note)
        # Check if duration suggests a dotted note
        if note.duration == 3:  # dotted quarter (with divisions=2)
            ET.SubElement(note_elem, "dot")
        elif note.duration == 6:  # dotted half (with divisions=2)
            ET.SubElement(note_elem, "dot")
        elif note.duration == 12:  # dotted whole (with divisions=2)
            ET.SubElement(note_elem, "dot")

        # Add voice
        if note.voice:
            voice = ET.SubElement(note_elem, "voice")
            voice.text = note.voice
        else:
            voice = ET.SubElement(note_elem, "voice")
            voice.text = "1"
