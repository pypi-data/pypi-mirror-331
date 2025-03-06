import xml.etree.ElementTree as ET
from descript_interchange import DescriptSequence
from descript_aaf import convert_to_aaf
import os


def convert_xml(path_to_xml, output_folder):
    root_path = os.path.dirname(path_to_xml)
    file_name = os.path.basename(path_to_xml)
    # Instantiate Element object
    tree = ET.parse(path_to_xml) 
    root = tree.getroot()


    # Extract top-level, sequence-related variables
    seq_dur = int(root[0][0].text)
    seq_name = root[0][1].text
    fps = int(root[0][4][0].text)
   
    # Instantiate sequence object
    seq = DescriptSequence(path_to_xml, fps, root_path, output_folder, seq_name, seq_dur, file_name)


    # Dictionary to store file references (linked to SourceFile instances)
    file_references = {}
    
    # Step 1: Extract Unique Source Files and Register with DescriptSequence
    for file_elem in root.findall(".//file"):
        file_id = file_elem.get("id")
        
        if file_id and file_id not in file_references:
            name = file_elem.findtext("name")
            duration = int(file_elem.findtext("duration"))
            
            # Extract timecode start value
            timecode_elem = file_elem.find(".//timecode/frame")
            start_timecode = timecode_elem.text if timecode_elem is not None else "UNKNOWN"
            start_timecode = int(start_timecode)

            # Register source file using DescriptSequence's helper function
            source_file = seq.add_source(name, duration, start_timecode)

            # Store reference to avoid duplicate creations
            file_references[file_id] = source_file

        seq.set_sequence_start_tc()

    # Step 2: Iterate Through Tracks in <video> and Add Them
    for track_elem in root.findall(".//video/track"):
        track = seq.add_track()  # Use helper function to create and attach track

        # Step 3: Iterate Through ClipItems (Chunks) Inside Each Track
        for clipitem in track_elem.findall("clipitem"):
            item_dur = int(clipitem.findtext("duration"))
            item_src_in = int(clipitem.findtext("in"))
            item_src_out = int(clipitem.findtext("out"))
            item_rec_in = int(clipitem.findtext("start"))
            item_rec_out = int(clipitem.findtext("end"))
            file_elem = clipitem.find("file")

            if file_elem is not None:
                file_id = file_elem.get("id")
                if file_id and file_id in file_references:
                    src_file = file_references[file_id]  # Retrieve existing SourceFile instance
                    
                    # Add chunk using Track's helper function
                    track.add_chunk(item_dur, src_file, item_src_in, item_rec_in, item_rec_out)

        
    aaf_conversion_status = convert_to_aaf(seq)
    if aaf_conversion_status:
        return True


