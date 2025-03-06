import aaf2
import os
from descript_interchange import DescriptSequence

def convert_to_aaf(descript_seq: DescriptSequence):
    result_filename, ext = os.path.splitext(descript_seq.file_name)
    result_file = os.path.join(descript_seq.output_folder, f"{result_filename}_CONVERTED.aaf")

    if os.path.exists(result_file):
        for i in range(1, 9999):
            result_file = os.path.join(descript_seq.output_folder, f"{result_filename}_CONVERTED_{i}.aaf")
            if os.path.exists(result_file):
                continue
            else:
                break

    with aaf2.open(result_file, "w") as f:

        # Create CompositionMob
        comp_mob = f.create.CompositionMob(descript_seq.seq_name)

        # Store references to created Master Mobs (to avoid duplicates)
        master_mobs = {}

        # Step 1: Extract and Create Source Mobs (Tape, File, and Master Mobs)
        for source in descript_seq.src_files:
            # Create Tape Mob
            tape_mob = f.create.SourceMob()
            tape_slot, tape_timecode_slot = tape_mob.create_tape_slots(source.name, descript_seq.fps, descript_seq.fps)
            
            tape_slot.segment.length = source.duration
            tape_timecode_slot.segment.start = source.start_tc
            f.content.mobs.append(tape_mob)

            # Create File Mob
            file_mob = f.create.SourceMob(source.name)
            loc = f.create.NetworkLocator()
            loc['URLString'].value = f"{source.name}"  # Update with actual path

            file_description = f.create.CDCIDescriptor()
            file_description.locator.append(loc)
            file_description['ComponentWidth'].value = 8
            file_description['HorizontalSubsampling'].value = 4
            file_description['ImageAspectRatio'].value = '5/4'
            file_description['StoredWidth'].value = 720
            file_description['StoredHeight'].value = 576
            file_description['FrameLayout'].value = 'FullFrame'
            file_description['VideoLineMap'].value = [0, 1]
            file_description['SampleRate'].value = descript_seq.fps
            file_description['Length'].value = source.duration

            file_mob.descriptor = file_description
            file_slot = file_mob.create_picture_slot(descript_seq.fps)
            tape_src_clip = tape_mob.create_source_clip(slot_id=1, length=source.duration)
            file_slot.segment.components.append(tape_src_clip)
            f.content.mobs.append(file_mob)

            # Create Master Mob
            master_mob = f.create.MasterMob()
            master_mob.name = source.name
            f.content.mobs.append(master_mob)

            # Attach File Mob to Master Mob
            
            clip = file_mob.create_source_clip(slot_id=1)
            slot = master_mob.create_picture_slot(descript_seq.fps)
            slot.segment.length = source.duration
            slot.segment.components.append(clip)

            # Store reference for later lookup
            master_mobs[source.name] = master_mob



        # Step 2: Iterate Over Tracks and Create Timeline Slots
        for track in descript_seq.tracks:

            # Create a new Sequence for this track
            track_sequence = f.create.Sequence(media_kind="picture")

            # Create a new Timeline Slot for the track in the Composition Mob
            timeline_slot = comp_mob.create_timeline_slot(descript_seq.fps)
            timeline_slot.segment = track_sequence  # Attach the track sequence to the slot
            if track.chunks[0].rec_in_tc != 0:
                filler_len = track.chunks[0].rec_in_tc
                filler_obj = f.create.Filler("picture", filler_len)
                track_sequence.components.append(filler_obj)
            
            # Track last expected end frame
            last_end = None


            # Step 3: Iterate Over Chunks in Order
            for i, chunk in enumerate(track.chunks):
                if chunk.src_file.name in master_mobs:
                    master_mob = master_mobs[chunk.src_file.name]

                    if chunk.rec_in_tc != last_end and not last_end is None:
                        filler_frames = chunk.rec_in_tc - last_end
                        filler = f.create.Filler("picture", filler_frames)
                        track_sequence.components.append(filler)
                        
                    adjusted_duration = chunk.rec_out_tc - chunk.rec_in_tc

                    # Step 3 - Create SourceClip
                    clip = master_mob.create_source_clip(slot_id=1, start=chunk.src_in_tc, length=adjusted_duration)

                    
                    # Append the Source Clip to the Sequence
                    track_sequence.components.append(clip)
                    last_end = chunk.rec_out_tc


                    
        master_tc1_slot = comp_mob.create_timeline_slot(descript_seq.fps)
        timecode = f.create.Timecode()
        timecode.start = descript_seq.start_tc
        master_tc1_slot.name = "TC1"
        master_tc1_slot.segment = timecode

        # Step 4: Attach Composition Mob to AAF
        f.content.mobs.append(comp_mob)
        return True
