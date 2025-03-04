import pathlib
from setuptools import setup
import sys

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# The version in the version file
__version__ = (HERE / "audiocat_clark/version").read_text()

# This call to setup() does all the work
setup(
    name="audiocat_clark",
    version=__version__,
    description = "Encrypted audio tunnel for secure chat, file transfer and remote shell on Linux.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ClarkFieseln/audiocat",
    author="Clark Fieseln",
    author_email="",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security",
    ],
    packages=["audiocat_clark"],
    package_data={
        '.': ['audiocat_clark/audiocat'],
    },
    data_files=[
        ('.', ['README.md']),
        ('audiocat', ['audiocat_clark/audiocat']),
        ('audiocat', ['audiocat_clark/killaudiocat.sh', 'audiocat_clark/mmack.sh', 'audiocat_clark/mmdata.sh', 'audiocat_clark/mmrx.sh', 'audiocat_clark/mmrxnopwd.sh', 'audiocat_clark/mmshellout.sh', 'audiocat_clark/mmtx.sh', 'audiocat_clark/mmtxfile.sh', 'audiocat_clark/install_dependencies.sh', 'audiocat_clark/mute_mic.sh', 'audiocat_clark/restore_mic.sh', 'audiocat_clark/version', 'audiocat_clark/stt.sh', 'audiocat_clark/tts.sh']),
        ('audiocat', ['audiocat_clark/gpg.src', 'audiocat_clark/gpgappend.src', 'audiocat_clark/rx.src', 'audiocat_clark/tx.src']),
        ('audiocat', ['audiocat_clark/audiocat.png']),
        ('audiocat/cfg', ['audiocat_clark/cfg/armor', 'audiocat_clark/cfg/baud', 'audiocat_clark/cfg/cipher_algo', 'audiocat_clark/cfg/confidence', 'audiocat_clark/cfg/end_msg', 'audiocat_clark/cfg/keepalive_time_sec', 'audiocat_clark/cfg/limit', 'audiocat_clark/cfg/logging_level', 'audiocat_clark/cfg/log_to_file', 'audiocat_clark/cfg/max_retransmissions', 'audiocat_clark/cfg/retransmission_timeout_sec', 'audiocat_clark/cfg/need_ack', 'audiocat_clark/cfg/preamble', 'audiocat_clark/cfg/probe_msg', 'audiocat_clark/cfg/probe_sleep', 'audiocat_clark/cfg/redundant_transmissions', 'audiocat_clark/cfg/send_delay_sec', 'audiocat_clark/cfg/show_rx_prompt', 'audiocat_clark/cfg/show_tx_prompt', 'audiocat_clark/cfg/split_tx_lines', 'audiocat_clark/cfg/start_msg', 'audiocat_clark/cfg/syncbyte', 'audiocat_clark/cfg/terminal', 'audiocat_clark/cfg/timeout_poll_sec', 'audiocat_clark/cfg/tmp_path', 'audiocat_clark/cfg/trailer', 'audiocat_clark/cfg/verbose', 'audiocat_clark/cfg/volume_microphone', 'audiocat_clark/cfg/volume_speaker_left', 'audiocat_clark/cfg/volume_speaker_right', 'audiocat_clark/cfg/install_dependencies', 'audiocat_clark/cfg/half_duplex', 'audiocat_clark/cfg/interface_index_stt_in', 'audiocat_clark/cfg/interface_index_tts_out', 'audiocat_clark/cfg/speech_to_text', 'audiocat_clark/cfg/text_to_speech', 'audiocat_clark/cfg/volume_stt_in', 'audiocat_clark/cfg/volume_tts_out']),
        ('audiocat/out', ['audiocat_clark/out/dummy']),
        ('audiocat/rx_files', ['audiocat_clark/rx_files/dummy']),
        ('audiocat/state', ['audiocat_clark/state/rx_receiving_file', 'audiocat_clark/state/seq_rx', 'audiocat_clark/state/seq_tx', 'audiocat_clark/state/seq_tx_acked', 'audiocat_clark/state/session_established', 'audiocat_clark/state/transmitter_started', 'audiocat_clark/state/tx_sending_file', 'audiocat_clark/state/tts_out']),
        ('audiocat/tmp', ['audiocat_clark/tmp/dummy'])
    ],    
    include_package_data=True,
    keywords=['chat','messenger','remote shell','remote control','reverse shell','file transfer','modem','audio','cryptography','encryption','security','cybersecurity','linux','gpg','minimodem','e2ee','data diode'],
    entry_points={
        "console_scripts": [
            "audiocat=audiocat_clark.audiocat:main",
        ]
    },
    project_urls={  # Optional
    'Source': 'https://github.com/ClarkFieseln/audiocat',
    },
)
