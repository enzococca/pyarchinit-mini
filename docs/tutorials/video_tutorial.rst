Video Tutorial
==============

Complete video tutorial demonstrating the PyArchInit-Mini web interface workflow.

.. raw:: html

   <div style="margin-bottom: 20px;">
     <video id="tutorialVideo" width="100%" controls>
       <source src="https://github.com/enzococca/pyarchinit-mini/raw/main/docs/tutorial_video/pyarchinit_tutorial_complete.webm" type="video/webm">
       Your browser does not support the video tag. <a href="https://github.com/enzococca/pyarchinit-mini/raw/main/docs/tutorial_video/pyarchinit_tutorial_complete.webm">Download the video</a>
     </video>

     <div style="margin-top: 10px; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
       <strong>Playback Speed:</strong>
       <button onclick="setSpeed(0.5)" style="margin: 2px; padding: 5px 10px; cursor: pointer;">0.5x</button>
       <button onclick="setSpeed(1)" style="margin: 2px; padding: 5px 10px; cursor: pointer;">1x</button>
       <button onclick="setSpeed(1.5)" style="margin: 2px; padding: 5px 10px; cursor: pointer;">1.5x</button>
       <button onclick="setSpeed(2)" style="margin: 2px; padding: 5px 10px; cursor: pointer; background-color: #4CAF50; color: white; font-weight: bold;">2x ⭐</button>
       <button onclick="setSpeed(3)" style="margin: 2px; padding: 5px 10px; cursor: pointer;">3x</button>
       <button onclick="setSpeed(4)" style="margin: 2px; padding: 5px 10px; cursor: pointer;">4x</button>
       <span id="currentSpeed" style="margin-left: 10px; font-weight: bold;">Current: 1x</span>
     </div>

     <script>
       function setSpeed(speed) {
         var video = document.getElementById('tutorialVideo');
         video.playbackRate = speed;
         document.getElementById('currentSpeed').textContent = 'Current: ' + speed + 'x';

         // Highlight active button
         var buttons = document.querySelectorAll('button[onclick^="setSpeed"]');
         buttons.forEach(function(btn) {
           btn.style.backgroundColor = '';
           btn.style.color = '';
           btn.style.fontWeight = '';
         });
         event.target.style.backgroundColor = '#4CAF50';
         event.target.style.color = 'white';
         event.target.style.fontWeight = 'bold';
       }
     </script>
   </div>

.. note::
   **Recommended viewing**: Watch at 2x-4x speed for faster viewing.

   Use the speed buttons above the video to adjust playback speed from 0.5x to 4x.

Video Information
-----------------

- **Duration**: ~12 minutes at 1x speed (~6 minutes at 2x speed)
- **Resolution**: 1920x1080 (Full HD)
- **File size**: 61 MB
- **Direct download**: `Download video <https://github.com/enzococca/pyarchinit-mini/raw/main/docs/tutorial_video/pyarchinit_tutorial_complete.webm>`_

Tutorial Content
----------------

This automated tutorial demonstrates a complete archaeological data entry workflow:

1. Periodization Management (3 entries)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Late Imperial period
- Late Imperial - Early Medieval transition
- Medieval period

2. Site Creation
~~~~~~~~~~~~~~~~

- Roman Forum Excavation site
- Location: Trench A
- Complete site metadata

3. Stratigraphic Units (5 entries with relationships)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **US 1001**: Stone wall foundation (Late Imperial)
- **US 1002**: Floor surface (Late Imperial) - *Abuts US 1001*
- **US 1003**: Destruction layer (Late Imperial-Early Medieval) - *Covers US 1002*
- **US 1004**: Pit cut (Medieval) - *Cuts US 1003*
- **US 1005**: Pit fill (Medieval) - *Fills US 1004*

Each unit includes:

- Stratigraphic and interpretative descriptions
- Chronological attribution
- Stratigraphic relationships

4. Archaeological Materials (3 entries)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Pottery**: African Red Slip ware bowl fragment (US 1002)
- **Metal**: Bronze coin (US 1003)
- **Glass**: Fragment of vessel rim (US 1003)

5. Harris Matrix Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Automatic stratigraphic matrix creation
- Visualization of temporal relationships

6. GraphML Export
~~~~~~~~~~~~~~~~~

- Export to GraphML format for advanced analysis
- Compatible with graph analysis tools

7. Site Summary
~~~~~~~~~~~~~~~

- Overview of all site data
- Statistics and visualizations

Features Demonstrated
---------------------

- **Thesaurus System**: Pre-populated controlled vocabularies
- **Form Validation**: Real-time data validation
- **Multi-tab Interface**: Organized data entry across tabs
- **Relationship Management**: Stratigraphic relationship tracking
- **Internationalization**: Bilingual data entry (Italian/English)
- **Export Capabilities**: GraphML format support

Technical Details
-----------------

- **Recording Method**: Automated Playwright browser automation
- **Typing Speed**: 0.5ms per character (accelerated for demonstration)
- **Database**: Clean SQLite database with initialized schema
- **Web Framework**: Flask with Flask-WTF forms
- **Authentication**: Secure login with session management

For PDF/EPUB Readers
--------------------

If you're reading this in PDF or EPUB format, the video cannot be embedded. You can:

1. **Download the video** from the GitHub repository:
   ``docs/tutorial_video/pyarchinit_tutorial_complete.webm``

2. **Access the HTML documentation** for interactive video playback:
   Visit the online documentation or open ``docs/VIDEO_TUTORIAL.html`` in your browser

3. **Direct link**: https://github.com/enzococca/pyarchinit-mini/blob/main/docs/tutorial_video/pyarchinit_tutorial_complete.webm

System Requirements
-------------------

To run PyArchInit-Mini as shown in the tutorial:

- Python 3.8+
- Modern web browser (Chrome, Firefox, Edge, Safari)
- 100MB free disk space
- Local or network database (SQLite, PostgreSQL, MySQL supported)

Installation
------------

.. code-block:: bash

   pip install pyarchinit-mini

   # Initialize database
   pyarchinit-mini-init

   # Start web interface
   python -m pyarchinit_mini.web_interface.app

Visit http://localhost:5001 to access the interface.

Support
-------

- **Documentation**: :doc:`../API_REFERENCE`
- **GitHub Issues**: https://github.com/enzococca/pyarchinit-mini/issues
- **Email**: enzococca@gmail.com

----

*Last updated: October 2025*

*PyArchInit-Mini version: 1.7.0+*
