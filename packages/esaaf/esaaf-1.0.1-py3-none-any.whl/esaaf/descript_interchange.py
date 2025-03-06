class SourceFile:
    def __init__(self, name, duration, start_tc):
        self.name = name
        self.duration = duration
        self.start_tc = start_tc


class Track:
    def __init__(self, slot_id):
        self.slot_id = slot_id
        self.chunks = []

    def add_chunk(self, duration, source_file, src_in_tc, rec_in_tc, rec_out_tc):
        chunk = VideoChunk(duration, source_file, src_in_tc, rec_in_tc, rec_out_tc)
        self.chunks.append(chunk)
        return chunk

class VideoChunk:
    def __init__(self, duration, src_file, src_in_tc, rec_in_tc, rec_out_tc):
        self.duration = duration
        self.src_in_tc = src_in_tc
        self.src_file = src_file
        self.rec_in_tc = rec_in_tc
        self.rec_out_tc = rec_out_tc
        

class DescriptSequence:
    def __init__(self, xml_path, fps, folder_path, output_folder, seq_name, duration, file_name):
        # put top level sequence info here
        self.file_name = file_name
        self.fps = fps
        self.xml_path = xml_path
        self.output_folder = output_folder
        self.seq_name = seq_name
        self.duration = duration
        self.root_path = folder_path
        self.src_files = []
        self.tracks = []
        self.available_slot_id = 1
        self.start_tc = None
    
    def add_source(self, name, duration, source_tc):
        source = SourceFile(name, duration, source_tc)
        self.src_files.append(source)
        return source
        
    def add_track(self):
        track = Track(self.available_slot_id)
        self.tracks.append(track)
        self.available_slot_id += 1
        return track
    
    def set_sequence_start_tc(self):
        timecodes = []
        for file in self.src_files:
            timecodes.append(file.start_tc)
        self.start_tc = min(timecodes)
        return min(timecodes)

