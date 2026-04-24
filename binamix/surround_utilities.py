# surround_channel_positions.py
# SADIE II angle mappings for typical surround configurations as defined by Dolby in the Dolby Atmos Production Suite. https://www.dolby.com/about/support/guide/speaker-setup-guides/
# The channel order and naming conventions come from the SMPTE ST 2067-8 standard and https://developer.dolby.com/globalassets/technology/atmos/additional-channels-for-immersive-audio.pdf
# Closest angles available are chosen from the SADIE II dataset for each channel.

# -----------------------------------------------------
class SurroundChannelPosition:
    def __init__(self, name, azi, ele):
        self.name = name
        self.azi = azi
        self.ele = ele

    def __repr__(self):
        return f"Name={self.name}, Azimuth={self.azi}°, Elevation={self.ele}°"

def supported_layouts():
    return ['7.1', '7.1.4', '7.1.2', '5.1', '5.1.4', '5.1.2', '9.1.4', '9.1.2', '9.1']

def get_channel_angles(layout):

    if layout == '7.1':

        # Note the SADIE II dataset does not have some standard surround angles across all subjects and BRIR/HRIR types
        # E.g. Standard angles are 30° and 330° for L and R respectively and are contained in all HRIRs but not in the BRIRs
    
        L = SurroundChannelPosition('L', 30, 0)       # Front Left 
        R = SurroundChannelPosition('R', 330, 0)      # Front Right 
        C = SurroundChannelPosition('C', 0, 0)        # Center
        Lfe = SurroundChannelPosition('Lfe', 0, 0)    # Low Frequency - Mapped to Center for Binaural Rendering
        Lss = SurroundChannelPosition('Lss', 90, 0)   # Side Surround Left
        Rss = SurroundChannelPosition('Rss', 270, 0)  # Side Surround Right
        Lrs = SurroundChannelPosition('Lrs', 135, 0)  # Surround Rear Left
        Rrs = SurroundChannelPosition('Rrs', 225, 0)  # Surround Rear Right

        channels = [L, R, C, Lfe, Lss, Rss, Lrs, Rrs]
    
        return channels
    
    elif layout == '7.1.4':

        # Note the SADIE II dataset does not have some standard surround angles across all subjects and BRIR/HRIR types
        # E.g. Standard angles are 30° and 330° for L and R respectively and are contained in all HRIRs but not in the BRIRs
     
        L = SurroundChannelPosition('L', 30, 0)         # Front Left 
        R = SurroundChannelPosition('R', 330, 0)        # Front Right  
        C = SurroundChannelPosition('C', 0, 0)          # Center
        Lfe = SurroundChannelPosition('Lfe', 0, 0)      # Low Frequency - Mapped to Center for Binaural Rendering
        Lss = SurroundChannelPosition('Lss', 90, 0)     # Surround Side Left
        Rss = SurroundChannelPosition('Rss', 270, 0)    # Surround Side Right
        Lrs = SurroundChannelPosition('Lrs', 135, 0)    # Surround Rear Left
        Rrs = SurroundChannelPosition('Rrs', 225, 0)    # Surround Rear Right
        Ltf = SurroundChannelPosition('Ltf', 45, 35.3)  # Top Front Left
        Rtf = SurroundChannelPosition('Rtf', 315, 35.3) # Top Front Right
        Ltb = SurroundChannelPosition('Ltb', 135, 35.3) # Top Rear Left
        Rtb = SurroundChannelPosition('Rtb', 225, 35.3) # Top Rear Right

        channels = [L, R, C, Lfe, Lss, Rss, Lrs, Rrs, Ltf, Rtf, Ltb, Rtb]
    
        return channels
    
    elif layout == '7.1.2':

        # Note the SADIE II dataset does not have some standard surround angles across all subjects and BRIR/HRIR types
        # E.g. Standard angles are 30° and 330° for L and R respectively and are contained in all HRIRs but not in the BRIRs
     
        L = SurroundChannelPosition('L', 30, 0)         # Front Left 
        R = SurroundChannelPosition('R', 330, 0)        # Front Right  
        C = SurroundChannelPosition('C', 0, 0)          # Center
        Lfe = SurroundChannelPosition('Lfe', 0, 0)      # Low Frequency - Mapped to Center for Binaural Rendering
        Lss = SurroundChannelPosition('Lss', 90, 0)     # Surround Side Left
        Rss = SurroundChannelPosition('Rss', 270, 0)    # Surround Side Right
        Lrs = SurroundChannelPosition('Lrs', 135, 0)    # Surround Rear Left
        Rrs = SurroundChannelPosition('Rrs', 225, 0)    # Surround Rear Right
        Ltf = SurroundChannelPosition('Ltf', 45, 35.3)  # Top Front Left
        Rtf = SurroundChannelPosition('Rtf', 315, 35.3) # Top Front Right
       

        channels = [L, R, C, Lfe, Lss, Rss, Lrs, Rrs, Ltf, Rtf]
    
        return channels

    elif layout == '5.1':

        # Note the SADIE II dataset does not have some standard surround angles across all subjects and BRIR/HRIR types
        # E.g. Standard angles are 30° and 330° for L and R respectively and are contained in all HRIRs but not in the BRIRs

        L = SurroundChannelPosition('L', 30, 0)         # Front Left  
        R = SurroundChannelPosition('R', 330, 0)        # Front Right 
        C = SurroundChannelPosition('C', 0, 0)          # Center
        Lfe = SurroundChannelPosition('Lfe', 0, 0)      # Low Frequency - Mapped to Center for Binaural Rendering
        Lrs = SurroundChannelPosition('Lrs', 120, 0)    # Surround Left 
        Rrs = SurroundChannelPosition('Rrs', 240, 0)    # Surround Right 

        channels = [L, R, C, Lfe, Lrs, Rrs]

        return channels

    elif layout == '5.1.4':

        # Note the SADIE II dataset does not have some standard surround angles across all subjects and BRIR/HRIR types
        # E.g. Standard angles are 30° and 330° for L and R respectively and are contained in all HRIRs but not in the BRIRs
 
        L = SurroundChannelPosition('L', 30, 0)         # Front Left 
        R = SurroundChannelPosition('R', 330, 0)        # Front Right 
        C = SurroundChannelPosition('C', 0, 0)          # Center
        Lfe = SurroundChannelPosition('Lfe', 0, 0)      # Low Frequency - Mapped to Center for Binaural Rendering
        Lrs = SurroundChannelPosition('Lrs', 120, 0)    # Surround Left 
        Rrs = SurroundChannelPosition('Rrs', 240, 0)    # Surround Right 
        Ltf = SurroundChannelPosition('Ltf', 45, 35.3)  # Top Front Left
        Rtf = SurroundChannelPosition('Rtf', 315, 35.3) # Top Front Right
        Ltb = SurroundChannelPosition('Ltb', 135, 35.3) # Top Rear Left
        Rtb = SurroundChannelPosition('Rtb', 225, 35.3) # Top Rear Right

        channels = [L, R, C, Lfe, Lrs, Rrs, Ltf, Rtf, Ltb, Rtb]

        return channels
    
    elif layout == '5.1.2':

        # Note the SADIE II dataset does not have some standard surround angles across all subjects and BRIR/HRIR types
        # E.g. Standard angles are 30° and 330° for L and R respectively and are contained in all HRIRs but not in the BRIRs
 
        L = SurroundChannelPosition('L', 30, 0)         # Front Left 
        R = SurroundChannelPosition('R', 330, 0)        # Front Right 
        C = SurroundChannelPosition('C', 0, 0)          # Center
        Lfe = SurroundChannelPosition('Lfe', 0, 0)      # Low Frequency - Mapped to Center for Binaural Rendering
        Lrs = SurroundChannelPosition('Lrs', 120, 0)    # Surround Left 
        Rrs = SurroundChannelPosition('Rrs', 240, 0)    # Surround Right 
        Ltf = SurroundChannelPosition('Ltf', 45, 35.3)  # Top Front Left
        Rtf = SurroundChannelPosition('Rtf', 315, 35.3) # Top Front Right

        channels = [L, R, C, Lfe, Lrs, Rrs, Ltf, Rtf]

        return channels
    
    elif layout == '9.1.4':

        # Note the SADIE II dataset does not have some standard surround angles across all subjects and BRIR/HRIR types
        # E.g. Standard angles are 30° and 330° for L and R respectively and are contained in all HRIRs but not in the BRIRs
     
        L = SurroundChannelPosition('L', 30, 0)         # Front Left 
        R = SurroundChannelPosition('R', 330, 0)        # Front Right  
        C = SurroundChannelPosition('C', 0, 0)          # Center
        Lfe = SurroundChannelPosition('Lfe', 0, 0)      # Low Frequency - Mapped to Center for Binaural Rendering
        Lss = SurroundChannelPosition('Lss', 90, 0)     # Surround Side Left
        Rss = SurroundChannelPosition('Rss', 270, 0)    # Surround Side Right
        Lrs = SurroundChannelPosition('Lrs', 135, 0)    # Surround Rear Left
        Rrs = SurroundChannelPosition('Rrs', 225, 0)    # Surround Rear Right
        Lw = SurroundChannelPosition('Lw', 60, 0)       # Wide Left
        Rw = SurroundChannelPosition('Rw', 300, 0)      # Wide Right
        Ltf = SurroundChannelPosition('Ltf', 45, 35.3)  # Top Front Left
        Rtf = SurroundChannelPosition('Rtf', 315, 35.3) # Top Front Right
        Ltb = SurroundChannelPosition('Ltb', 135, 35.3) # Top Rear Left
        Rtb = SurroundChannelPosition('Rtb', 225, 35.3) # Top Rear Right

        channels = [L, R, C, Lfe, Lss, Rss, Lrs, Rrs, Lw, Rw, Ltf, Rtf, Ltb, Rtb]
    
        return channels
    
    elif layout == '9.1.2':

        # Note the SADIE II dataset does not have some standard surround angles across all subjects and BRIR/HRIR types
        # E.g. Standard angles are 30° and 330° for L and R respectively and are contained in all HRIRs but not in the BRIRs
     
        L = SurroundChannelPosition('L', 30, 0)         # Front Left 
        R = SurroundChannelPosition('R', 330, 0)        # Front Right  
        C = SurroundChannelPosition('C', 0, 0)          # Center
        Lfe = SurroundChannelPosition('Lfe', 0, 0)      # Low Frequency - Mapped to Center for Binaural Rendering
        Lss = SurroundChannelPosition('Lss', 90, 0)     # Surround Side Left
        Rss = SurroundChannelPosition('Rss', 270, 0)    # Surround Side Right
        Lrs = SurroundChannelPosition('Lrs', 135, 0)    # Surround Rear Left
        Rrs = SurroundChannelPosition('Rrs', 225, 0)    # Surround Rear Right
        Lw = SurroundChannelPosition('Lw', 60, 0)       # Wide Left
        Rw = SurroundChannelPosition('Rw', 300, 0)      # Wide Right
        Ltf = SurroundChannelPosition('Ltf', 45, 35.3)  # Top Front Left
        Rtf = SurroundChannelPosition('Rtf', 315, 35.3) # Top Front Right

        channels = [L, R, C, Lfe, Lss, Rss, Lrs, Rrs, Lw, Rw, Ltf, Rtf]
    
        return channels
    
    elif layout == '9.1':

        # Note the SADIE II dataset does not have some standard surround angles across all subjects and BRIR/HRIR types
        # E.g. Standard angles are 30° and 330° for L and R respectively and are contained in all HRIRs but not in the BRIRs
     
        L = SurroundChannelPosition('L', 30, 0)         # Front Left 
        R = SurroundChannelPosition('R', 330, 0)        # Front Right  
        C = SurroundChannelPosition('C', 0, 0)          # Center
        Lfe = SurroundChannelPosition('Lfe', 0, 0)      # Low Frequency - Mapped to Center for Binaural Rendering
        Lss = SurroundChannelPosition('Lss', 90, 0)     # Surround Side Left
        Rss = SurroundChannelPosition('Rss', 270, 0)    # Surround Side Right
        Lrs = SurroundChannelPosition('Lrs', 135, 0)    # Surround Rear Left
        Rrs = SurroundChannelPosition('Rrs', 225, 0)    # Surround Rear Right
        Lw = SurroundChannelPosition('Lw', 60, 0)       # Wide Left
        Rw = SurroundChannelPosition('Rw', 300, 0)      # Wide Right

        channels = [L, R, C, Lfe, Lss, Rss, Lrs, Rrs, Lw, Rw]
    
        return channels


    else:

        raise ValueError(f"Unsupported layout: {layout} - Valid layouts are {supported_layouts()}")

