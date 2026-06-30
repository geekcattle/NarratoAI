import streamlit as st
import os
import shutil
import json
from uuid import uuid4
from app.config import config
from app.services import voice
from app.models.schema import AudioVolumeDefaults
from app.utils import utils


INDEXTTS_REFERENCE_AUDIO_SOURCE_DIR = "/Users/viccy/Downloads/tts-mp3-clone/mp3"
INDEXTTS_REFERENCE_AUDIO_COPY_SUBDIR = "indextts_refs"
INDEXTTS_REFERENCE_AUDIO_MAP = [
    ("yingshijieshuo-zh-male.mp3", "影视解说", "Film Narration"),
    ("maikeashe-zh-male.mp3", "麦克阿瑟", "Macintosh"),
    ("dong-yuhui-zh-male.mp3", "董宇辉", "Dong Yuhui"),
    ("fangzhenren-ad-fake-news-zh-male.mp3", "仿真人", "Realistic Human"),
    ("fengyin-jilupian-jieshuo-zh-male.mp3", "风吟纪录片解说", "Fengyin Documentary Narration"),
    ("guwo-dianying-jieshuo-zh-male.mp3", "顾我电影解说", "Guwo Film Narration"),
    ("jia-xiaojun-final-zh-male.mp3", "贾小军", "Jia Xiaojun"),
    ("junshi-zh-male.mp3", "军事解说", "Military Narration"),
    ("qi-tongwei-v2-zh-male.mp3", "祁同伟", "Qi Tongwei"),
    ("saima-niang-mambo-oye-zh-female.mp3", "赛马娘曼波欧耶版", "Uma Musume Mambo Oye Version"),
    ("shejian-shangde-zhongguo-zh-male.mp3", "舌尖上的中国", "A Bite of China"),
    ("xiaoming-jianmo-zh-male.mp3", "小明剑魔", "Xiaoming Sword Demon"),
    ("xin-youxi-jieshuo-zh-male.mp3", "新游戏解说", "New Game Narration"),
    ("xinzhong-zhicheng-zh-male.mp3", "心中之城", "City in the Heart"),
    ("alex-chikna-en-male.mp3", "亚历克斯", "Alex Chikna"),
    ("alle-en-unknown.mp3", "艾莉", "ALLE"),
    ("calm-normal-en-unknown.mp3", "沉稳男声", "Calm Normal"),
    ("donald-j-trump-noise-reduction-en-male.mp3", "唐纳德·特朗普", "Donald J. Trump"),
    ("elite-en-unknown.mp3", "精英男声", "ELITE"),
    ("horror-en-unknown.mp3", "惊悚男声", "Horror"),
    ("meiqu-kelong-en-unknown.mp3", "美式男声", "US Clone"),
    ("sarah-en-female.mp3", "莎拉", "Sarah"),
]
INDEXTTS_REFERENCE_AUDIO_EXTENSIONS = (".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg")
BGM_RESOURCE_DIR = "/Users/viccy/Downloads/tts-mp3-clone/bgms-safe"
BGM_TRACKS_JSON = os.path.join(BGM_RESOURCE_DIR, "tracks.json")
BGM_UPLOAD_SUBDIR = "uploaded_bgms"
BGM_AUDIO_EXTENSIONS = (".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg")
LOCAL_TTS_ENGINES = {
    config.INDEXTTS_ENGINE,
    config.INDEXTTS2_ENGINE,
    config.OMNIVOICE_ENGINE,
}


def get_soulvoice_voices():
    """获取 SoulVoice 语音列表"""
    # 检查是否配置了 SoulVoice API key
    api_key = config.soulvoice.get("api_key", "")
    if not api_key:
        return []

    # 只返回一个 SoulVoice 选项，音色通过输入框自定义
    return ["soulvoice:custom"]


def get_tts_engine_options(tr=lambda key: key):
    """获取TTS引擎选项"""
    engine_options = {
        config.INDEXTTS_ENGINE: config.INDEXTTS_DISPLAY_NAME,
        config.INDEXTTS2_ENGINE: config.INDEXTTS2_DISPLAY_NAME,
        config.OMNIVOICE_ENGINE: config.OMNIVOICE_DISPLAY_NAME,
        "edge_tts": "Edge TTS",
        "qwen3_tts": tr("Tongyi Qwen3 TTS"),
        "tencent_tts": tr("Tencent Cloud TTS"),
        "doubaotts": tr("Doubao TTS"),
        "azure_speech": "Azure Speech Services"
    }

    return {
        engine: format_tts_engine_option(engine, display_name, tr)
        for engine, display_name in engine_options.items()
    }


def get_tts_engine_deployment_label(tts_engine, tr=lambda key: key):
    """获取TTS引擎部署类型标签"""
    if tts_engine in LOCAL_TTS_ENGINES:
        return tr("Local Deployment")

    return tr("Cloud Service")


def format_tts_engine_option(tts_engine, display_name, tr=lambda key: key):
    """格式化TTS引擎下拉显示名"""
    deployment_label = get_tts_engine_deployment_label(tts_engine, tr)
    return f"{display_name} [{deployment_label}]"


def get_tts_engine_descriptions(tr=lambda key: key):
    """获取TTS引擎详细描述"""
    return {
        "edge_tts": {
            "title": "Edge TTS",
            "features": tr("Edge TTS features"),
            "use_case": tr("Edge TTS use case"),
            "registration": None
        },
        "azure_speech": {
            "title": "Azure Speech Services",
            "features": tr("Azure Speech Services features"),
            "use_case": tr("Azure Speech Services use case"),
            "registration": "https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/SpeechServices"
        },
        "tencent_tts": {
            "title": tr("Tencent Cloud TTS"),
            "features": tr("Tencent Cloud TTS features"),
            "use_case": tr("Tencent Cloud TTS use case"),
            "registration": "https://console.cloud.tencent.com/tts"
        },
        "qwen3_tts": {
            "title": tr("Tongyi Qwen3 TTS"),
            "features": tr("Tongyi Qwen3 TTS features"),
            "use_case": tr("High-quality Chinese speech synthesis use case"),
            "registration": "https://dashscope.aliyuncs.com/"
        },
        config.INDEXTTS_ENGINE: {
            "title": config.INDEXTTS_DISPLAY_NAME,
            "features": tr("IndexTTS features"),
            "use_case": tr("IndexTTS use case"),
            "registration": None
        },
        config.INDEXTTS2_ENGINE: {
            "title": config.INDEXTTS2_DISPLAY_NAME,
            "features": tr("IndexTTS2 features"),
            "use_case": tr("IndexTTS2 use case"),
            "registration": None
        },
        config.OMNIVOICE_ENGINE: {
            "title": config.OMNIVOICE_DISPLAY_NAME,
            "features": tr("OmniVoice features"),
            "use_case": tr("OmniVoice use case"),
            "registration": None
        },
        "doubaotts": {
            "title": tr("Doubao TTS"),
            "features": tr("Doubao TTS features"),
            "use_case": tr("High-quality Chinese speech synthesis use case"),
            "registration": "https://www.volcengine.com/product/voice-tech"
        }
    }


def infer_indextts_reference_audio_language(filename):
    """根据文件名推断参考音频语言"""
    lower_filename = filename.lower()
    if "-zh-" in lower_filename:
        return "zh"
    if "-en-" in lower_filename:
        return "en"
    return "unknown"


def get_indextts_reference_audio_options():
    """获取本地 IndexTTS-1.5 参考音频选项"""
    options = []
    mapped_files = set()

    for filename, zh_name, en_name in INDEXTTS_REFERENCE_AUDIO_MAP:
        audio_path = os.path.join(INDEXTTS_REFERENCE_AUDIO_SOURCE_DIR, filename)
        if os.path.isfile(audio_path):
            options.append({
                "filename": filename,
                "path": audio_path,
                "zh": zh_name,
                "en": en_name,
                "language": infer_indextts_reference_audio_language(filename),
            })
            mapped_files.add(filename)

    if os.path.isdir(INDEXTTS_REFERENCE_AUDIO_SOURCE_DIR):
        for filename in sorted(os.listdir(INDEXTTS_REFERENCE_AUDIO_SOURCE_DIR)):
            if filename in mapped_files:
                continue
            if not filename.lower().endswith(INDEXTTS_REFERENCE_AUDIO_EXTENSIONS):
                continue
            audio_path = os.path.join(INDEXTTS_REFERENCE_AUDIO_SOURCE_DIR, filename)
            if not os.path.isfile(audio_path):
                continue
            fallback_name = os.path.splitext(filename)[0]
            options.append({
                "filename": filename,
                "path": audio_path,
                "zh": fallback_name,
                "en": fallback_name,
                "language": infer_indextts_reference_audio_language(filename),
            })

    return options


def format_indextts_reference_audio_option(option):
    """格式化 IndexTTS-1.5 参考音频下拉显示名"""
    zh_name = option.get("zh", "")
    en_name = option.get("en", "")
    language = option.get("language", "unknown")
    ui_language = str(st.session_state.get("ui_language", "zh-CN")).lower()

    if ui_language.startswith("en"):
        display_name = en_name or zh_name or option.get("filename", "")
        language_labels = {
            "zh": "Chinese",
            "en": "English",
        }
    else:
        display_name = zh_name or en_name or option.get("filename", "")
        language_labels = {
            "zh": "中文",
            "en": "英文",
        }

    language_label = language_labels.get(language)
    if not language_label:
        return display_name

    return f"{display_name} ({language_label})"


def get_indextts_reference_audio_index(options, saved_reference_audio):
    """根据已保存的参考音频文件匹配下拉选项索引"""
    if not options:
        return 0

    saved_filename = os.path.basename(saved_reference_audio or "")
    for index, option in enumerate(options):
        if option["filename"] == saved_filename:
            return index

    return 0


def copy_indextts_reference_audio(source_path):
    """复制一份参考音频到项目存储目录，并返回复制后的路径"""
    if not source_path or not os.path.isfile(source_path):
        return ""

    target_dir = utils.storage_dir(INDEXTTS_REFERENCE_AUDIO_COPY_SUBDIR, create=True)
    target_path = os.path.join(target_dir, os.path.basename(source_path))

    if os.path.abspath(source_path) == os.path.abspath(target_path):
        return target_path

    should_copy = True
    if os.path.exists(target_path):
        should_copy = os.path.getsize(source_path) != os.path.getsize(target_path)

    if should_copy:
        shutil.copy2(source_path, target_path)

    return target_path


def load_bgm_tracks_metadata():
    """读取 BGM 资源描述信息。"""
    if not os.path.isfile(BGM_TRACKS_JSON):
        return {}

    try:
        with open(BGM_TRACKS_JSON, "r", encoding="utf-8") as f:
            tracks = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(tracks, list):
        return {}

    metadata = {}
    for track in tracks:
        if not isinstance(track, dict):
            continue
        filename = track.get("fileName")
        if filename:
            metadata[filename] = track

    return metadata


def get_bgm_resource_options():
    """获取 BGM 资源目录中的音频选项。"""
    options = []
    metadata = load_bgm_tracks_metadata()
    added_files = set()

    for filename, track in metadata.items():
        audio_path = os.path.join(BGM_RESOURCE_DIR, filename)
        if not os.path.isfile(audio_path):
            continue

        options.append({
            "filename": filename,
            "path": audio_path,
            "title": track.get("title") or os.path.splitext(filename)[0],
            "style": track.get("style", ""),
            "category": track.get("category", ""),
        })
        added_files.add(filename)

    if os.path.isdir(BGM_RESOURCE_DIR):
        for filename in sorted(os.listdir(BGM_RESOURCE_DIR)):
            if filename in added_files:
                continue
            if not filename.lower().endswith(BGM_AUDIO_EXTENSIONS):
                continue

            audio_path = os.path.join(BGM_RESOURCE_DIR, filename)
            if not os.path.isfile(audio_path):
                continue

            options.append({
                "filename": filename,
                "path": audio_path,
                "title": os.path.splitext(filename)[0],
                "style": "",
                "category": "",
            })

    return options


def format_bgm_resource_option(option):
    """格式化 BGM 资源下拉显示名。"""
    title = option.get("title") or os.path.splitext(option.get("filename", ""))[0]
    style = option.get("style", "")
    category = option.get("category", "")

    if style:
        return f"{title} ({style})"
    if category:
        return f"{title} ({category})"
    return title


def get_bgm_resource_index(options, saved_bgm_file):
    """根据已保存的 BGM 文件匹配下拉选项索引。"""
    if not options:
        return 0

    saved_filename = os.path.basename(saved_bgm_file or "")
    for index, option in enumerate(options):
        if option["filename"] == saved_filename:
            return index

    return 0


def get_audio_mime_type(audio_path):
    """根据音频文件扩展名返回 MIME 类型"""
    extension = os.path.splitext(audio_path or "")[1].lower()
    if extension == ".wav":
        return "audio/wav"
    if extension == ".flac":
        return "audio/flac"
    if extension == ".ogg":
        return "audio/ogg"
    if extension == ".m4a":
        return "audio/mp4"
    if extension == ".aac":
        return "audio/aac"
    return "audio/mp3"


def render_reference_audio_preview_button(reference_audio, key, tr, preview_state_key="indextts_reference_audio_preview_path"):
    """渲染参考音频试听按钮"""
    can_preview = bool(reference_audio and os.path.isfile(reference_audio))
    if st.button(
        " ",
        key=key,
        icon=":material/play_arrow:",
        help=tr("Preview Reference Audio Help"),
        disabled=not can_preview,
        use_container_width=True,
    ):
        st.session_state[preview_state_key] = reference_audio


def render_indextts_reference_audio_selector(tr, tts_config, key_prefix):
    """渲染 IndexTTS 系列共用的参考音频选择器。"""
    saved_reference_audio = tts_config.get("reference_audio", "")
    reference_audio_source_options = {
        tr("Select from Resource Directory"): "resource",
        tr("Upload Reference Audio"): "upload",
    }
    reference_audio_source_labels = list(reference_audio_source_options.keys())
    saved_reference_audio_source = tts_config.get("reference_audio_source", "resource")
    if saved_reference_audio_source not in reference_audio_source_options.values():
        saved_reference_audio_source = "resource"
    default_reference_audio_source_label = next(
        label
        for label, source_value in reference_audio_source_options.items()
        if source_value == saved_reference_audio_source
    )

    st.markdown(f"**{tr('Reference Audio Path')}**")
    reference_audio_source_label = st.pills(
        tr("Reference Audio Source"),
        options=reference_audio_source_labels,
        selection_mode="single",
        default=default_reference_audio_source_label,
        key=f"{key_prefix}_reference_audio_source_selection",
        help=tr("Reference Audio Source Help"),
        label_visibility="collapsed",
        width="stretch",
    )
    if not reference_audio_source_label:
        reference_audio_source_label = default_reference_audio_source_label
    reference_audio_source = reference_audio_source_options[reference_audio_source_label]

    reference_audio = saved_reference_audio
    preview_state_key = f"{key_prefix}_reference_audio_preview_path"
    reference_audio_options = get_indextts_reference_audio_options()
    if reference_audio_source == "resource" and reference_audio_options:
        selected_audio_index = get_indextts_reference_audio_index(reference_audio_options, saved_reference_audio)
        select_col, preview_col = st.columns([5, 1])
        with select_col:
            selected_audio_option = reference_audio_options[st.selectbox(
                tr("Reference Audio Path"),
                options=range(len(reference_audio_options)),
                index=selected_audio_index,
                format_func=lambda x: format_indextts_reference_audio_option(reference_audio_options[x]),
                help=tr("Reference Audio Path Help"),
                label_visibility="collapsed",
                key=f"{key_prefix}_reference_audio_select",
            )]
        reference_audio = copy_indextts_reference_audio(selected_audio_option["path"])
        with preview_col:
            render_reference_audio_preview_button(
                reference_audio,
                f"{key_prefix}_resource_reference_audio_preview",
                tr,
                preview_state_key=preview_state_key,
            )
    elif reference_audio_source == "resource":
        st.warning(tr("No Reference Audio Resources Found"))

    if reference_audio_source == "upload":
        if saved_reference_audio_source != "upload":
            reference_audio = ""
        upload_col, preview_col = st.columns([5, 1])
        with upload_col:
            uploaded_file = st.file_uploader(
                tr("Upload Reference Audio File"),
                type=["wav", "mp3"],
                help=tr("Upload Reference Audio Help"),
                label_visibility="collapsed",
                key=f"{key_prefix}_reference_audio_upload",
            )

        if uploaded_file is not None:
            target_dir = utils.storage_dir(INDEXTTS_REFERENCE_AUDIO_COPY_SUBDIR, create=True)
            audio_path = os.path.join(target_dir, f"uploaded_{uploaded_file.name}")
            with open(audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            reference_audio = audio_path
            st.success(tr("Audio uploaded").format(path=audio_path))
        with preview_col:
            render_reference_audio_preview_button(
                reference_audio,
                f"{key_prefix}_upload_reference_audio_preview",
                tr,
                preview_state_key=preview_state_key,
            )

    preview_audio_path = st.session_state.get(preview_state_key, "")
    if preview_audio_path == reference_audio and os.path.isfile(preview_audio_path):
        with open(preview_audio_path, "rb") as audio_file:
            st.audio(audio_file.read(), format=get_audio_mime_type(preview_audio_path))

    return reference_audio_source, reference_audio


def render_bgm_preview_button(bgm_file, key, tr):
    """渲染 BGM 试听按钮。"""
    can_preview = bool(bgm_file and os.path.isfile(bgm_file))
    if st.button(
        " ",
        key=key,
        icon=":material/play_arrow:",
        help=tr("Preview Background Music Help"),
        disabled=not can_preview,
        use_container_width=True,
    ):
        st.session_state["bgm_preview_path"] = bgm_file


def is_valid_azure_voice_name(voice_name: str) -> bool:
    """检查是否为有效的Azure音色名称格式"""
    if not voice_name or not isinstance(voice_name, str):
        return False

    voice_name = voice_name.strip()

    # Azure音色名称通常格式为: [语言]-[地区]-[名称]Neural
    # 例如: zh-CN-YunzeNeural, en-US-AvaMultilingualNeural
    import re
    pattern = r'^[a-z]{2}-[A-Z]{2}-\w+Neural$'
    return bool(re.match(pattern, voice_name))


def render_audio_panel(tr):
    """渲染音频设置面板"""
    with st.container(border=True):
        st.write(tr("Audio Settings"))

        # 渲染TTS设置
        render_tts_settings(tr)

    # 背景音乐独立成框，放在音频设置下方
    render_bgm_panel(tr)


def render_bgm_panel(tr):
    """渲染背景音乐设置面板"""
    with st.container(border=True):
        render_bgm_settings(tr)


def render_tts_settings(tr):
    """渲染TTS(文本转语音)设置"""

    # 1. TTS引擎选择器
    # st.subheader("TTS引擎选择")

    engine_options = get_tts_engine_options(tr)
    engine_descriptions = get_tts_engine_descriptions(tr)

    # 获取保存的TTS引擎设置
    saved_tts_engine = config.normalize_tts_engine_name(
        config.ui.get("tts_engine", config.INDEXTTS_ENGINE)
    )

    # 确保保存的引擎在可用选项中
    if saved_tts_engine not in engine_options:
        saved_tts_engine = config.INDEXTTS_ENGINE

    # TTS引擎选择下拉框
    selected_engine = st.selectbox(
        tr("Select TTS Engine"),
        options=list(engine_options.keys()),
        format_func=lambda x: engine_options[x],
        index=list(engine_options.keys()).index(saved_tts_engine),
        help=tr("Select TTS Engine Help")
    )

    # 保存TTS引擎选择
    config.ui["tts_engine"] = selected_engine
    st.session_state['tts_engine'] = selected_engine

    # 2. 显示引擎详细说明
    if selected_engine in engine_descriptions:
        desc = engine_descriptions[selected_engine]

        with st.expander(tr("TTS Engine Details").format(engine=desc['title']), expanded=False):
            st.markdown(f"**{tr('Features')}:** {desc['features']}")
            st.markdown(f"**{tr('Use Case')}:** {desc['use_case']}")

            if desc['registration']:
                st.markdown(f"**{tr('Registration URL')}:** [{desc['registration']}]({desc['registration']})")

    # 3. 根据选择的引擎渲染对应的配置界面
    # st.subheader("引擎配置")

    if selected_engine == "edge_tts":
        render_edge_tts_settings(tr)
    elif selected_engine == "azure_speech":
        render_azure_speech_settings(tr)
    elif selected_engine == "soulvoice":
        render_soulvoice_engine_settings(tr)
    elif selected_engine == "tencent_tts":
        render_tencent_tts_settings(tr)
    elif selected_engine == "qwen3_tts":
        render_qwen3_tts_settings(tr)
    elif selected_engine == config.INDEXTTS_ENGINE:
        render_indextts_tts_settings(tr)
    elif selected_engine == config.INDEXTTS2_ENGINE:
        render_indextts2_tts_settings(tr)
    elif selected_engine == config.OMNIVOICE_ENGINE:
        render_omnivoice_tts_settings(tr)
    elif selected_engine == "doubaotts":
        render_doubaotts_settings(tr)

    # 4. 试听功能
    render_voice_preview_new(tr, selected_engine)


def render_edge_tts_settings(tr):
    """渲染 Edge TTS 引擎设置"""
    # 获取 Edge TTS 支持的全部语言和音色
    edge_voices = voice.get_all_edge_voices()

    # 创建友好的显示名称
    friendly_names = {}
    for v in edge_voices:
        friendly_names[v] = v.replace("Female", tr("Female")).replace("Male", tr("Male")).replace("Neural", "")

    # 获取保存的语音设置
    saved_voice_name = config.ui.get("edge_voice_name", "zh-CN-XiaoxiaoNeural-Female")

    # 确保保存的音色在可用列表中
    if saved_voice_name not in friendly_names:
        # 选择与UI语言匹配的第一个语音
        for v in edge_voices:
            if v.lower().startswith(st.session_state.get("ui_language", "zh-CN").lower()):
                saved_voice_name = v
                break
        else:
            # 如果没找到匹配的，使用第一个
            saved_voice_name = edge_voices[0] if edge_voices else ""

    # 音色选择下拉框
    selected_friendly_name = st.selectbox(
        tr("Voice Selection"),
        options=list(friendly_names.values()),
        index=list(friendly_names.keys()).index(saved_voice_name) if saved_voice_name in friendly_names else 0,
        help=tr("Select Edge TTS Voice")
    )

    # 获取实际的语音名称
    voice_name = list(friendly_names.keys())[
        list(friendly_names.values()).index(selected_friendly_name)
    ]

    # 显示音色信息
    with st.expander(tr("Edge TTS Voice Description"), expanded=False):
        st.write(tr("Loaded voice count").format(count=len(edge_voices)))
        for v in edge_voices:
            gender = tr("Female Voice") if "Female" in v else tr("Male Voice")
            name = v.replace("-Female", "").replace("-Male", "").replace("Neural", "")
            st.write(f"• {name} ({gender})")

    config.ui["edge_voice_name"] = voice_name
    config.ui["voice_name"] = voice_name  # 兼容性

    # 音量调节
    voice_volume = st.slider(
        tr("Voice Volume"),
        min_value=0,
        max_value=100,
        value=int(config.ui.get("edge_volume", 80)),
        step=1,
        help=tr("Voice Volume Help Percent")
    )
    config.ui["edge_volume"] = voice_volume
    st.session_state['voice_volume'] = voice_volume / 100.0

    # 语速调节
    voice_rate = st.slider(
        tr("Voice Rate"),
        min_value=0.5,
        max_value=2.0,
        value=config.ui.get("edge_rate", 1.0),
        step=0.1,
        help=tr("Voice Rate Help 0.5-2.0")
    )
    config.ui["edge_rate"] = voice_rate
    st.session_state['voice_rate'] = voice_rate

    # 语调调节
    voice_pitch = st.slider(
        tr("Voice Pitch"),
        min_value=-50,
        max_value=50,
        value=int(config.ui.get("edge_pitch", 0)),
        step=5,
        help=tr("Voice Pitch Help Percent")
    )
    config.ui["edge_pitch"] = voice_pitch
    # 转换为比例值
    st.session_state['voice_pitch'] = 1.0 + (voice_pitch / 100.0)


def render_azure_speech_settings(tr):
    """渲染 Azure Speech Services 引擎设置"""
    # 服务区域配置
    azure_speech_region = st.text_input(
        tr("Service Region"),
        value=config.azure.get("speech_region", ""),
        placeholder=tr("Service Region Placeholder"),
        help=tr("Azure Service Region Help")
    )

    # API Key配置
    azure_speech_key = st.text_input(
        "API Key",
        value=config.azure.get("speech_key", ""),
        type="password",
        help=tr("Azure Speech Key Help")
    )

    # 保存Azure配置
    config.azure["speech_region"] = azure_speech_region
    config.azure["speech_key"] = azure_speech_key

    # 音色名称输入框
    saved_voice_name = config.ui.get("azure_voice_name", "zh-CN-XiaoxiaoMultilingualNeural")

    # 音色名称输入
    voice_name = st.text_input(
        tr("Voice Name"),
        value=saved_voice_name,
        help=tr("Azure Voice Name Help"),
        placeholder="zh-CN-YunzeNeural"
    )

    # 显示常用音色示例
    with st.expander(tr("Common Voice Reference"), expanded=False):
        st.write(f"**{tr('Chinese Voices')}:**")
        st.write(f"• zh-CN-XiaoxiaoMultilingualNeural ({tr('Female Voice')}, {tr('Multilingual')})")
        st.write(f"• zh-CN-YunzeNeural ({tr('Male Voice')})")
        st.write(f"• zh-CN-YunxiNeural ({tr('Male Voice')})")
        st.write(f"• zh-CN-XiaochenNeural ({tr('Female Voice')})")
        st.write("")
        st.write(f"**{tr('English Voices')}:**")
        st.write(f"• en-US-AndrewMultilingualNeural ({tr('Male Voice')}, {tr('Multilingual')})")
        st.write(f"• en-US-AvaMultilingualNeural ({tr('Female Voice')}, {tr('Multilingual')})")
        st.write(f"• en-US-BrianMultilingualNeural ({tr('Male Voice')}, {tr('Multilingual')})")
        st.write(f"• en-US-EmmaMultilingualNeural ({tr('Female Voice')}, {tr('Multilingual')})")
        st.write("")
        st.info(tr("Azure Voices Docs Notice"))

    # 快速选择按钮
    st.write(f"**{tr('Quick Select')}:**")
    cols = st.columns(3)
    with cols[0]:
        if st.button(tr("Chinese Female Voice"), help="zh-CN-XiaoxiaoMultilingualNeural"):
            voice_name = "zh-CN-XiaoxiaoMultilingualNeural"
            st.rerun()
    with cols[1]:
        if st.button(tr("Chinese Male Voice"), help="zh-CN-YunzeNeural"):
            voice_name = "zh-CN-YunzeNeural"
            st.rerun()
    with cols[2]:
        if st.button(tr("English Female Voice"), help="en-US-AvaMultilingualNeural"):
            voice_name = "en-US-AvaMultilingualNeural"
            st.rerun()

    # 验证音色名称并显示状态
    if voice_name.strip():
        # 检查是否为有效的Azure音色格式
        if is_valid_azure_voice_name(voice_name):
            st.success(tr("Voice name valid").format(voice=voice_name))
        else:
            st.warning(tr("Voice name format may be invalid").format(voice=voice_name))
            st.info(tr("Azure voice name format notice"))

    # 保存配置
    config.ui["azure_voice_name"] = voice_name
    config.ui["voice_name"] = voice_name  # 兼容性

    # 音量调节
    voice_volume = st.slider(
        tr("Voice Volume"),
        min_value=0,
        max_value=100,
        value=int(config.ui.get("azure_volume", 80)),
        step=1,
        help=tr("Voice Volume Help Percent")
    )
    config.ui["azure_volume"] = voice_volume
    st.session_state['voice_volume'] = voice_volume / 100.0

    # 语速调节
    voice_rate = st.slider(
        tr("Voice Rate"),
        min_value=0.5,
        max_value=2.0,
        value=config.ui.get("azure_rate", 1.0),
        step=0.1,
        help=tr("Voice Rate Help 0.5-2.0")
    )
    config.ui["azure_rate"] = voice_rate
    st.session_state['voice_rate'] = voice_rate

    # 语调调节
    voice_pitch = st.slider(
        tr("Voice Pitch"),
        min_value=-50,
        max_value=50,
        value=int(config.ui.get("azure_pitch", 0)),
        step=5,
        help=tr("Voice Pitch Help Percent")
    )
    config.ui["azure_pitch"] = voice_pitch
    # 转换为比例值
    st.session_state['voice_pitch'] = 1.0 + (voice_pitch / 100.0)

    # 显示配置状态
    if azure_speech_region and azure_speech_key:
        st.success(tr("Azure Speech Services configured"))
    elif not azure_speech_region:
        st.warning(tr("Please configure service region"))
    elif not azure_speech_key:
        st.warning(tr("Please configure API Key"))


def render_tencent_tts_settings(tr):
    """渲染腾讯云 TTS 引擎设置"""
    # Secret ID 输入
    secret_id = st.text_input(
        "Secret ID",
        value=config.tencent.get("secret_id", ""),
        help=tr("Tencent Secret ID Help")
    )

    # Secret Key 输入
    secret_key = st.text_input(
        "Secret Key",
        value=config.tencent.get("secret_key", ""),
        type="password",
        help=tr("Tencent Secret Key Help")
    )

    # 地域选择
    region_options = [
        "ap-beijing",
        "ap-shanghai",
        "ap-guangzhou",
        "ap-chengdu",
        "ap-nanjing",
        "ap-singapore",
        "ap-hongkong"
    ]
    
    saved_region = config.tencent.get("region", "ap-beijing")
    if saved_region not in region_options:
        region_options.append(saved_region)
    
    region = st.selectbox(
        tr("Service Region"),
        options=region_options,
        index=region_options.index(saved_region),
        help=tr("Tencent Service Region Help")
    )

    # 音色选择
    voice_type_options = {
        "501000": "智斌 - 阅读男声",
        "501001": "智兰 - 资讯女声",
        "501002": "智菊 - 阅读女声",
        "501003": "智宇 - 阅读男声",
        "501004": "月华 - 聊天女声",
        "501005": "飞镜 - 聊天男声",
        "501006": "千嶂 - 聊天男声",
        "501007": "浅草 - 聊天男声",
        "501008": "WeJames - 外语男声",
        "501009": "WeWinny - 外语女声",
        "601008": "爱小豪 - 聊天男声",
        "601009": "爱小芊 - 聊天女声",
        "601010": "爱小娇 - 聊天女声",
        "601011": "爱小川 - 聊天男声",
        "601012": "爱小璟 - 特色女声",
        "601013": "爱小伊 - 阅读女声",
        "601014": "爱小简 - 聊天男声",
        "101050": "WeJack - 英文男声",
        "101055": "智付 - 通用女声",
        "101013": "智辉 - 新闻男声",
        "101019": "智彤 - 粤语女声",
        "101030": "智柯 - 通用男声",
        "101054": "智友 - 通用男声",
        "101027": "智梅 - 通用女声",
        "101026": "智希 - 通用女声",
        "101004": "智云 - 通用男声",
        "101015": "智萌 - 男童声",
        "101011": "智燕 - 新闻女声",
        "101001": "智瑜 - 情感女声",
        "101021": "智瑞 - 新闻男声",
        "101016": "智甜 - 女童声"
    }
    
    saved_voice_type = config.ui.get("tencent_voice_type", "101001")
    if saved_voice_type not in voice_type_options:
        voice_type_options[saved_voice_type] = f"{tr('Custom Voice')} ({saved_voice_type})"
    
    selected_voice_display = st.selectbox(
        tr("Voice Selection"),
        options=list(voice_type_options.values()),
        index=list(voice_type_options.keys()).index(saved_voice_type),
        help=tr("Select Tencent TTS Voice")
    )
    
    # 获取实际的音色ID
    voice_type = list(voice_type_options.keys())[
        list(voice_type_options.values()).index(selected_voice_display)
    ]
    
    # 语速调节
    voice_rate = st.slider(
        tr("Voice Rate"),
        min_value=0.5,
        max_value=2.0,
        value=config.ui.get("tencent_rate", 1.0),
        step=0.1,
        help=tr("Voice Rate Help 0.5-2.0")
    )
    
    config.ui["voice_name"] = saved_voice_type  # 兼容性
    
    # 显示音色说明
    with st.expander(tr("Tencent Cloud TTS Voice Description"), expanded=False):
        st.write(f"**{tr('Female Voices')}:**")
        female_voices = [(k, v) for k, v in voice_type_options.items() if "女声" in v]
        for voice_id, voice_desc in female_voices[:6]:  # 显示前6个
            st.write(f"• {voice_desc} (ID: {voice_id})")
        
        st.write("")
        st.write(f"**{tr('Male Voices')}:**")
        male_voices = [(k, v) for k, v in voice_type_options.items() if "男声" in v]
        for voice_id, voice_desc in male_voices:
            st.write(f"• {voice_desc} (ID: {voice_id})")
        
        st.write("")
        st.info(tr("Tencent More Voices Notice"))
    
    # 保存配置
    config.tencent["secret_id"] = secret_id
    config.tencent["secret_key"] = secret_key
    config.tencent["region"] = region
    config.ui["tencent_voice_type"] = voice_type
    config.ui["tencent_rate"] = voice_rate
    config.ui["voice_name"] = saved_voice_type #兼容性


def render_qwen3_tts_settings(tr):
    """渲染 Qwen3 TTS 设置"""
    api_key = st.text_input(
        "API Key",
        value=config.tts_qwen.get("api_key", ""),
        type="password",
        help=tr("Qwen DashScope API Key Help")
    )

    model_name = st.text_input(
        tr("TTS Model Name"),
        value=config.tts_qwen.get("model_name", "qwen3-tts-flash"),
        help=tr("Qwen TTS Model Help")
    )

    # Qwen3 TTS 音色选项 - 中文名: 英文参数
    voice_options = {
        "芊悦": "Cherry",
        "晨煦": "Ethan",
        "不吃鱼": "Nofish",
        "詹妮弗": "Jennifer",
        "甜茶": "Ryan",
        "卡捷琳娜": "Katerina",
        "墨讲师": "Elias",
        "上海-阿珍": "Jada",
        "北京-晓东": "Dylan",
        "四川-晴儿": "Sunny",
        "南京-老李": "Li",
        "陕西-秦川": "Marcus",
        "闽南-阿杰": "Roy",
        "天津-李彼得": "Peter",
        "粤语-阿强": "Rocky",
        "粤语-阿清": "Kiki",
        "四川-程川": "Eric"
    }
    
    # 显示给用户的中文名称列表
    display_names = list(voice_options.keys())
    saved_voice_param = config.ui.get("qwen_voice_type", "Cherry")
    
    # 如果保存的英文参数不在选项中，查找对应的中文名称
    saved_display_name = "芊悦"  # 默认值
    for chinese_name, english_param in voice_options.items():
        if english_param == saved_voice_param:
            saved_display_name = chinese_name
            break
    
    # 如果保存的音色不在选项中，添加到自定义选项
    if saved_display_name not in display_names:
        display_names.append(saved_display_name)
        voice_options[saved_display_name] = saved_voice_param

    selected_display_name = st.selectbox(
        tr("Voice Selection"),
        options=display_names,
        index=display_names.index(saved_display_name) if saved_display_name in display_names else 0,
        help=tr("Select Qwen3 TTS Voice")
    )
    
    # 获取对应的英文参数
    voice_type = voice_options.get(selected_display_name, "Cherry")

    voice_rate = st.slider(
        tr("Voice Rate"),
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help=tr("Voice Rate Help 0.5-2.0")
    )

    # 保存配置
    config.tts_qwen["api_key"] = api_key
    config.tts_qwen["model_name"] = model_name
    config.ui["qwen_voice_type"] = voice_type
    config.ui["qwen3_rate"] = voice_rate
    config.ui["voice_name"] = voice_type #兼容性


def render_indextts_tts_settings(tr):
    """渲染 IndexTTS-1.5 TTS 设置"""
    # API 地址配置
    api_url = st.text_input(
        tr("API URL"),
        value=config.indextts.get("api_url", "http://127.0.0.1:8081/tts"),
        help=tr("IndexTTS API URL Help")
    )
    
    reference_audio_source, reference_audio = render_indextts_reference_audio_selector(
        tr,
        config.indextts,
        "indextts",
    )
    
    # 推理模式
    infer_mode_options = [
        ("普通推理", tr("Standard Inference")),
        ("快速推理", tr("Fast Inference")),
    ]
    infer_mode_index = 0 if config.indextts.get("infer_mode", "普通推理") == "普通推理" else 1
    infer_mode = infer_mode_options[st.selectbox(
        tr("Inference Mode"),
        options=range(len(infer_mode_options)),
        index=infer_mode_index,
        format_func=lambda x: infer_mode_options[x][1],
        help=tr("Inference Mode Help")
    )][0]
    
    # 高级参数折叠面板
    with st.expander(tr("Advanced Parameters"), expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            temperature = st.slider(
                tr("Sampling Temperature"),
                min_value=0.1,
                max_value=2.0,
                value=float(config.indextts.get("temperature", 1.0)),
                step=0.1,
                help=tr("Sampling Temperature Help")
            )
            
            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=float(config.indextts.get("top_p", 0.8)),
                step=0.05,
                help=tr("Top P Help")
            )
            
            top_k = st.slider(
                "Top K",
                min_value=0,
                max_value=100,
                value=int(config.indextts.get("top_k", 30)),
                step=5,
                help=tr("Top K Help")
            )
        
        with col2:
            num_beams = st.slider(
                tr("Num Beams"),
                min_value=1,
                max_value=10,
                value=int(config.indextts.get("num_beams", 3)),
                step=1,
                help=tr("Num Beams Help")
            )
            
            repetition_penalty = st.slider(
                tr("Repetition Penalty"),
                min_value=1.0,
                max_value=20.0,
                value=float(config.indextts.get("repetition_penalty", 10.0)),
                step=0.5,
                help=tr("Repetition Penalty Help")
            )
            
            do_sample = st.checkbox(
                tr("Enable Sampling"),
                value=config.indextts.get("do_sample", True),
                help=tr("Enable Sampling Help")
            )
    
    # 显示使用说明
    with st.expander(tr("IndexTTS Usage Instructions Title"), expanded=False):
        st.markdown(tr("IndexTTS Usage Instructions"))
    
    # 保存配置
    config.indextts["api_url"] = api_url
    config.indextts["reference_audio_source"] = reference_audio_source
    config.indextts["reference_audio"] = reference_audio
    config.indextts["infer_mode"] = infer_mode
    config.indextts["temperature"] = temperature
    config.indextts["top_p"] = top_p
    config.indextts["top_k"] = top_k
    config.indextts["num_beams"] = num_beams
    config.indextts["repetition_penalty"] = repetition_penalty
    config.indextts["do_sample"] = do_sample
    
    # 保存 voice_name 用于兼容性
    if reference_audio:
        config.ui["voice_name"] = f"{config.INDEXTTS_VOICE_PREFIX}{reference_audio}"


def render_indextts2_tts_settings(tr):
    """渲染 IndexTTS-2 TTS 设置"""
    api_url = st.text_input(
        tr("API URL"),
        value=config.indextts2.get("api_url", "http://192.168.3.6:7863/tts"),
        help=tr("IndexTTS2 API URL Help")
    )

    reference_audio_source, reference_audio = render_indextts_reference_audio_selector(
        tr,
        config.indextts2,
        "indextts2",
    )

    emotion_mode_options = [
        ("speaker", tr("Emotion Mode Speaker")),
        ("audio", tr("Emotion Mode Audio")),
        ("vector", tr("Emotion Mode Vector")),
        ("text", tr("Emotion Mode Text")),
    ]
    saved_emotion_mode = config.indextts2.get("emotion_mode", "speaker")
    emotion_mode_values = [item[0] for item in emotion_mode_options]
    if saved_emotion_mode not in emotion_mode_values:
        saved_emotion_mode = "speaker"

    with st.expander(tr("IndexTTS2 Emotion Parameters"), expanded=False):
        emotion_mode = emotion_mode_options[st.selectbox(
            tr("Emotion Mode"),
            options=range(len(emotion_mode_options)),
            index=emotion_mode_values.index(saved_emotion_mode),
            format_func=lambda x: emotion_mode_options[x][1],
            help=tr("Emotion Mode Help"),
        )][0]

        emotion_alpha = st.slider(
            tr("Emotion Alpha"),
            min_value=0.0,
            max_value=1.0,
            value=float(config.indextts2.get("emotion_alpha", 0.65)),
            step=0.05,
            help=tr("Emotion Alpha Help"),
        )

        emotion_audio = config.indextts2.get("emotion_audio", "")
        emotion_text = config.indextts2.get("emotion_text", "")
        if emotion_mode == "audio":
            emotion_audio_col, emotion_preview_col = st.columns([5, 1])
            with emotion_audio_col:
                emotion_audio = st.text_input(
                    tr("Emotion Reference Audio Path"),
                    value=emotion_audio,
                    help=tr("Emotion Reference Audio Path Help"),
                )
            with emotion_preview_col:
                render_reference_audio_preview_button(
                    emotion_audio,
                    "indextts2_emotion_audio_preview",
                    tr,
                    preview_state_key="indextts2_emotion_audio_preview_path",
                )
            preview_audio_path = st.session_state.get("indextts2_emotion_audio_preview_path", "")
            if preview_audio_path == emotion_audio and os.path.isfile(preview_audio_path):
                with open(preview_audio_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format=get_audio_mime_type(preview_audio_path))
        elif emotion_mode == "text":
            emotion_text = st.text_input(
                tr("Emotion Text"),
                value=emotion_text,
                help=tr("Emotion Text Help"),
                placeholder=tr("Emotion Text Placeholder"),
            )

        use_random = st.checkbox(
            tr("Use Random Emotion"),
            value=bool(config.indextts2.get("use_random", False)),
            help=tr("Use Random Emotion Help"),
        )

        emotion_vector_defaults = {
            "vec_happy": 0.0,
            "vec_angry": 0.0,
            "vec_sad": 0.0,
            "vec_afraid": 0.0,
            "vec_disgusted": 0.0,
            "vec_melancholic": 0.0,
            "vec_surprised": 0.0,
            "vec_calm": 0.8,
        }
        emotion_vector_labels = {
            "vec_happy": tr("Emotion Happy"),
            "vec_angry": tr("Emotion Angry"),
            "vec_sad": tr("Emotion Sad"),
            "vec_afraid": tr("Emotion Afraid"),
            "vec_disgusted": tr("Emotion Disgusted"),
            "vec_melancholic": tr("Emotion Melancholic"),
            "vec_surprised": tr("Emotion Surprised"),
            "vec_calm": tr("Emotion Calm"),
        }
        emotion_vector_values = {}
        if emotion_mode == "vector":
            vec_cols = st.columns(2)
            for index, (field, default_value) in enumerate(emotion_vector_defaults.items()):
                with vec_cols[index % 2]:
                    emotion_vector_values[field] = st.slider(
                        emotion_vector_labels[field],
                        min_value=0.0,
                        max_value=1.0,
                        value=float(config.indextts2.get(field, default_value)),
                        step=0.05,
                    )
        else:
            emotion_vector_values = {
                field: float(config.indextts2.get(field, default_value))
                for field, default_value in emotion_vector_defaults.items()
            }

    with st.expander(tr("Advanced Parameters"), expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            temperature = st.slider(
                tr("Sampling Temperature"),
                min_value=0.1,
                max_value=2.0,
                value=float(config.indextts2.get("temperature", 0.8)),
                step=0.1,
                help=tr("Sampling Temperature Help")
            )

            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=float(config.indextts2.get("top_p", 0.8)),
                step=0.05,
                help=tr("Top P Help")
            )

            top_k = st.slider(
                "Top K",
                min_value=0,
                max_value=100,
                value=int(config.indextts2.get("top_k", 30)),
                step=5,
                help=tr("Top K Help")
            )

            max_text_tokens_per_segment = st.slider(
                tr("Max Text Tokens Per Segment"),
                min_value=20,
                max_value=600,
                value=int(config.indextts2.get("max_text_tokens_per_segment", 120)),
                step=10,
                help=tr("Max Text Tokens Per Segment Help")
            )

        with col2:
            num_beams = st.slider(
                tr("Num Beams"),
                min_value=1,
                max_value=10,
                value=int(config.indextts2.get("num_beams", 3)),
                step=1,
                help=tr("Num Beams Help")
            )

            repetition_penalty = st.slider(
                tr("Repetition Penalty"),
                min_value=0.1,
                max_value=20.0,
                value=float(config.indextts2.get("repetition_penalty", 10.0)),
                step=0.1,
                help=tr("Repetition Penalty Help")
            )

            max_mel_tokens = st.slider(
                tr("Max Mel Tokens"),
                min_value=50,
                max_value=1815,
                value=int(config.indextts2.get("max_mel_tokens", 1500)),
                step=10,
                help=tr("Max Mel Tokens Help")
            )

    with st.expander(tr("IndexTTS2 Usage Instructions Title"), expanded=False):
        st.markdown(tr("IndexTTS2 Usage Instructions"))

    config.indextts2["api_url"] = api_url
    config.indextts2["reference_audio_source"] = reference_audio_source
    config.indextts2["reference_audio"] = reference_audio
    config.indextts2["emotion_mode"] = emotion_mode
    config.indextts2["emotion_audio"] = emotion_audio
    config.indextts2["emotion_alpha"] = emotion_alpha
    config.indextts2["emotion_text"] = emotion_text
    config.indextts2["use_random"] = use_random
    config.indextts2["max_text_tokens_per_segment"] = max_text_tokens_per_segment
    for field, value in emotion_vector_values.items():
        config.indextts2[field] = value
    config.indextts2["temperature"] = temperature
    config.indextts2["top_p"] = top_p
    config.indextts2["top_k"] = top_k
    config.indextts2["num_beams"] = num_beams
    config.indextts2["repetition_penalty"] = repetition_penalty
    config.indextts2["max_mel_tokens"] = max_mel_tokens

    if reference_audio:
        config.ui["voice_name"] = f"{config.INDEXTTS2_VOICE_PREFIX}{reference_audio}"
    st.session_state['voice_rate'] = 1.0
    st.session_state['voice_pitch'] = 1.0


def render_omnivoice_tts_settings(tr):
    """渲染 OmniVoice TTS 设置"""
    omnivoice_config = config.omnivoice

    api_url = st.text_input(
        tr("API URL"),
        value=omnivoice_config.get("api_url", "http://127.0.0.1:7866/tts"),
        help=tr("OmniVoice API URL Help"),
    )

    language = st.text_input(
        tr("OmniVoice Language Code"),
        value=omnivoice_config.get("language", "zh"),
        help=tr("OmniVoice Language Code Help"),
        placeholder="zh",
    )

    mode_options = [
        ("auto", tr("OmniVoice Mode Auto")),
        ("voice_design", tr("OmniVoice Mode Voice Design")),
        ("voice_clone", tr("OmniVoice Mode Voice Clone")),
    ]
    mode_values = [item[0] for item in mode_options]
    saved_mode = omnivoice_config.get("mode", "auto")
    if saved_mode not in mode_values:
        saved_mode = "auto"

    mode = mode_options[st.selectbox(
        tr("OmniVoice Generation Mode"),
        options=range(len(mode_options)),
        index=mode_values.index(saved_mode),
        format_func=lambda x: mode_options[x][1],
        help=tr("OmniVoice Generation Mode Help"),
    )][0]

    instruct = omnivoice_config.get("instruct", "")
    reference_audio_source = omnivoice_config.get("reference_audio_source", "resource")
    reference_audio = omnivoice_config.get("reference_audio", "")
    ref_text = omnivoice_config.get("ref_text", "")

    if mode == "voice_design":
        instruct = st.text_area(
            tr("OmniVoice Instruct"),
            value=instruct,
            help=tr("OmniVoice Instruct Help"),
            placeholder=tr("OmniVoice Instruct Placeholder"),
            height=80,
        )
    elif mode == "voice_clone":
        reference_audio_source, reference_audio = render_indextts_reference_audio_selector(
            tr,
            omnivoice_config,
            "omnivoice",
        )
        ref_text = st.text_area(
            tr("OmniVoice Reference Text"),
            value=ref_text,
            help=tr("OmniVoice Reference Text Help"),
            placeholder=tr("OmniVoice Reference Text Placeholder"),
            height=90,
        )

    with st.expander(tr("Advanced Parameters"), expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            num_step = st.slider(
                "Num Step",
                min_value=4,
                max_value=64,
                value=int(omnivoice_config.get("num_step", 32)),
                step=1,
                help=tr("OmniVoice Num Step Help"),
            )
            guidance_scale = st.slider(
                "Guidance Scale",
                min_value=0.1,
                max_value=10.0,
                value=float(omnivoice_config.get("guidance_scale", 2.0)),
                step=0.1,
                help=tr("OmniVoice Guidance Scale Help"),
            )
            voice_rate = st.slider(
                tr("Voice Rate"),
                min_value=0.5,
                max_value=2.0,
                value=float(omnivoice_config.get("speed", 1.0)),
                step=0.1,
                help=tr("Voice Rate Help 0.5-2.0"),
            )
        with col2:
            saved_duration = omnivoice_config.get("duration", "")
            duration_value = float(saved_duration) if saved_duration not in (None, "") else 0.0
            duration = st.number_input(
                tr("OmniVoice Duration"),
                min_value=0.0,
                max_value=120.0,
                value=duration_value,
                step=0.5,
                help=tr("OmniVoice Duration Help"),
            )
            denoise = st.checkbox(
                tr("OmniVoice Denoise"),
                value=bool(omnivoice_config.get("denoise", True)),
                help=tr("OmniVoice Denoise Help"),
            )
            postprocess_output = st.checkbox(
                tr("OmniVoice Postprocess Output"),
                value=bool(omnivoice_config.get("postprocess_output", True)),
                help=tr("OmniVoice Postprocess Output Help"),
            )
            preprocess_prompt = st.checkbox(
                tr("OmniVoice Preprocess Prompt"),
                value=bool(omnivoice_config.get("preprocess_prompt", True)),
                help=tr("OmniVoice Preprocess Prompt Help"),
            )

    with st.expander(tr("OmniVoice Usage Instructions Title"), expanded=False):
        st.markdown(tr("OmniVoice Usage Instructions"))

    config.omnivoice["api_url"] = api_url
    config.omnivoice["language"] = language
    config.omnivoice["mode"] = mode
    config.omnivoice["instruct"] = instruct
    config.omnivoice["reference_audio_source"] = reference_audio_source
    config.omnivoice["reference_audio"] = reference_audio
    config.omnivoice["ref_text"] = ref_text
    config.omnivoice["num_step"] = num_step
    config.omnivoice["guidance_scale"] = guidance_scale
    config.omnivoice["speed"] = voice_rate
    config.omnivoice["duration"] = duration if duration > 0 else ""
    config.omnivoice["denoise"] = denoise
    config.omnivoice["postprocess_output"] = postprocess_output
    config.omnivoice["preprocess_prompt"] = preprocess_prompt

    if mode == "voice_clone" and reference_audio:
        config.ui["voice_name"] = f"{config.OMNIVOICE_VOICE_PREFIX}{reference_audio}"
    else:
        config.ui["voice_name"] = f"{config.OMNIVOICE_VOICE_PREFIX}{mode}"
    st.session_state["voice_rate"] = voice_rate
    st.session_state["voice_pitch"] = 1.0


def render_doubaotts_settings(tr):
    """渲染豆包语音 TTS 2.0 设置"""
    # API Key 输入
    api_key = st.text_input(
        "API Key",
        value=config.doubaotts.get("api_key", ""),
        type="password",
        help=tr("Volcengine API Key Help")
    )

    # Resource ID (模型版本) 输入
    resource_id_options = {
        "seed-tts-2.0": "豆包语音合成大模型 2.0",
        "seed-icl-2.0": "豆包声音复刻大模型 2.0",
    }
    saved_resource_id = config.doubaotts.get("resource_id", "seed-tts-2.0")
    if saved_resource_id not in resource_id_options:
        saved_resource_id = "seed-tts-2.0"

    resource_id = st.selectbox(
        tr("Model Version (Resource ID)"),
        options=list(resource_id_options.keys()),
        format_func=lambda x: resource_id_options[x],
        index=list(resource_id_options.keys()).index(saved_resource_id),
        help=tr("Doubao Resource ID Help")
    )

    # 音色选择
    voice_options = {
            # 通用场景
            "zh_female_vv_uranus_bigtts": "Vivi 2.0 (多语种)",
            "zh_female_xiaohe_uranus_bigtts": "小何 2.0",
            "zh_male_m191_uranus_bigtts": "云舟 2.0",
            "zh_male_taocheng_uranus_bigtts": "小天 2.0",
            "zh_male_liufei_uranus_bigtts": "刘飞 2.0",
            "zh_female_sophie_uranus_bigtts": "魅力苏菲 2.0",
            "zh_female_qingxinnvsheng_uranus_bigtts": "清新女声 2.0",
            "zh_female_cancan_uranus_bigtts": "知性灿灿 2.0",
            "zh_female_sajiaoxuemei_uranus_bigtts": "撒娇学妹 2.0",
            "zh_female_tianmeixiaoyuan_uranus_bigtts": "甜美小源 2.0",
            "zh_female_tianmeitaozi_uranus_bigtts": "甜美桃子 2.0",
            "zh_female_shuangkuaisisi_uranus_bigtts": "爽快思思 2.0",
            "zh_female_peiqi_uranus_bigtts": "佩奇猪 2.0 (抖音同款)",
            "zh_female_linjianvhai_uranus_bigtts": "邻家女孩 2.0",
            "zh_male_shaonianzixin_uranus_bigtts": "少年梓辛/Brayan 2.0",
            "zh_male_sunwukong_uranus_bigtts": "猴哥 2.0",
            "zh_female_yingyujiaoxue_uranus_bigtts": "Tina 老师 2.0 (中英)",
            "zh_female_kefunvsheng_uranus_bigtts": "暖阳女声 2.0",
            "zh_female_xiaoxue_uranus_bigtts": "儿童绘本 2.0",
            "zh_male_dayi_uranus_bigtts": "大壹 2.0",
            "zh_female_mizai_uranus_bigtts": "黑猫侦探社咪仔 2.0",
            "zh_female_jitangnv_uranus_bigtts": "鸡汤女 2.0",
            "zh_female_meilinvyou_uranus_bigtts": "魅力女友 2.0",
            "zh_female_liuchangnv_uranus_bigtts": "流畅女声 2.0",
            "zh_male_ruyayichen_uranus_bigtts": "儒雅逸辰 2.0",
            "en_male_tim_uranus_bigtts": "Tim (美式英语)",
            "en_female_dacey_uranus_bigtts": "Dacey (美式英语)",
            "en_female_stokie_uranus_bigtts": "Stokie (美式英语)",
            "zh_female_wenroumama_uranus_bigtts": "温柔妈妈 2.0",
            "zh_male_jieshuoxiaoming_uranus_bigtts": "解说小明 2.0",
            "zh_female_tvbnv_uranus_bigtts": "TVB 女声 2.0",
            "zh_male_yizhipiannan_uranus_bigtts": "译制片男 2.0",
            "zh_female_qiaopinv_uranus_bigtts": "俏皮女声 2.0",
            "zh_female_zhishuaiyingzi_uranus_bigtts": "直率英子 2.0 (抖音同款)",
            "zh_male_linjiananhai_uranus_bigtts": "邻家男孩 2.0",
            "zh_male_silang_uranus_bigtts": "四郎 2.0 (抖音同款)",
            "zh_male_ruyaqingnian_uranus_bigtts": "儒雅青年 2.0 (番茄小说同款)",
            "zh_male_qingcang_uranus_bigtts": "擎苍 2.0 (抖音同款)",
            "zh_male_xionger_uranus_bigtts": "熊二 2.0 (抖音同款)",
            "zh_female_yingtaowanzi_uranus_bigtts": "樱桃丸子 2.0 (抖音同款)",
            "zh_male_wennuanahu_uranus_bigtts": "温暖阿虎/Alvin 2.0",
            "zh_male_naiqimengwa_uranus_bigtts": "奶气萌娃 2.0 (剪映同款)",
            "zh_female_popo_uranus_bigtts": "婆婆 2.0 (抖音同款)",
            "zh_female_gaolengyujie_uranus_bigtts": "高冷御姐 2.0",
            "zh_male_aojiaobazong_uranus_bigtts": "傲娇霸总 2.0",
            "zh_male_lanyinmianbao_uranus_bigtts": "懒音绵宝 2.0",
            "zh_male_fanjuanqingnian_uranus_bigtts": "反卷青年 2.0",
            "zh_female_wenroushunv_uranus_bigtts": "温柔淑女 2.0 (番茄小说同款)",
            "zh_female_gufengshaoyu_uranus_bigtts": "古风少御 2.0",
            "zh_male_huolixiaoge_uranus_bigtts": "活力小哥 2.0",
            "zh_male_baqiqingshu_uranus_bigtts": "霸气青叔 2.0 (番茄小说同款)",
            "zh_male_xuanyijieshuo_uranus_bigtts": "悬疑解说 2.0 (抖音同款)",
            "zh_female_mengyatou_uranus_bigtts": "萌丫头/Cutey 2.0",
            "zh_female_tiexinnvsheng_uranus_bigtts": "贴心女声/Candy 2.0",
            "zh_female_jitangmei_uranus_bigtts": "鸡汤妹妹/Hope 2.0 (抖音同款)",
            "zh_male_cixingjieshuonan_uranus_bigtts": "磁性解说男声/Morgan 2.0 (抖音同款)",
            "zh_male_liangsangmengzai_uranus_bigtts": "亮嗓萌仔 2.0",
            "zh_female_kailangjiejie_uranus_bigtts": "开朗姐姐 2.0",
            "zh_male_gaolengchenwen_uranus_bigtts": "高冷沉稳 2.0 (猫箱同款)",
            "zh_male_shenyeboke_uranus_bigtts": "深夜播客 2.0",
            "zh_male_lubanqihao_uranus_bigtts": "鲁班七号 2.0 (抖音同款)",
            "zh_female_jiaochuannv_uranus_bigtts": "娇喘女声 2.0 (抖音同款)",
            "zh_female_linxiao_uranus_bigtts": "林潇 2.0 (抖音同款)",
            "zh_female_lingling_uranus_bigtts": "玲玲姐姐 2.0 (抖音同款)",
            "zh_female_chunribu_uranus_bigtts": "春日部姐姐 2.0 (抖音同款)",
            "zh_male_tangseng_uranus_bigtts": "唐僧 2.0 (抖音同款)",
            "zh_male_zhuangzhou_uranus_bigtts": "庄周 2.0 (抖音同款)",
            "zh_male_kailangdidi_uranus_bigtts": "开朗弟弟 2.0 (抖音同款)",
            "zh_male_zhubajie_uranus_bigtts": "猪八戒 2.0 (豆包同款)",
            "zh_female_ganmaodianyin_uranus_bigtts": "感冒电音姐姐 2.0 (抖音同款)",
            "zh_female_chanmeinv_uranus_bigtts": "谄媚女声 2.0 (抖音同款)",
            "zh_female_nvleishen_uranus_bigtts": "女雷神 2.0 (豆包同款)",
            "zh_female_qinqienv_uranus_bigtts": "亲切女声 2.0 (豆包同款)",
            "zh_male_kuailexiaodong_uranus_bigtts": "快乐小东 2.0 (豆包同款)",
            "zh_male_kailangxuezhang_uranus_bigtts": "开朗学长 2.0 (豆包同款)",
            "zh_male_youyoujunzi_uranus_bigtts": "悠悠君子 2.0 (豆包同款)",
            "zh_female_wenjingmaomao_uranus_bigtts": "文静毛毛 2.0 (豆包同款)",
            "zh_female_zhixingnv_uranus_bigtts": "知性女声 2.0",
            "zh_male_qingshuangnanda_uranus_bigtts": "清爽男大 2.0 (豆包同款)",
            "zh_male_yuanboxiaoshu_uranus_bigtts": "渊博小叔 2.0",
            "zh_male_yangguangqingnian_uranus_bigtts": "阳光青年 2.0",
            "zh_female_qingchezizi_uranus_bigtts": "清澈梓梓 2.0",
            "zh_female_tianmeiyueyue_uranus_bigtts": "甜美悦悦 2.0",
            "zh_female_xinlingjitang_uranus_bigtts": "心灵鸡汤 2.0",
            "zh_male_wenrouxiaoge_uranus_bigtts": "温柔小哥 2.0",
            "zh_female_roumeinvyou_uranus_bigtts": "柔美女友 2.0",
            "zh_male_dongfanghaoran_uranus_bigtts": "东方浩然 2.0",
            "zh_female_wenrouxiaoya_uranus_bigtts": "温柔小雅 2.0",
            "zh_male_tiancaitongsheng_uranus_bigtts": "天才童声 2.0",
            "zh_female_wuzetian_uranus_bigtts": "武则天 2.0 (剪映同款)",
            "zh_female_gujie_uranus_bigtts": "顾姐 2.0 (抖音同款)",
            "zh_male_guanggaojieshuo_uranus_bigtts": "广告解说 2.0 (剪映同款)",
            "zh_female_shaoergushi_uranus_bigtts": "少儿故事 2.0",
            # ICL 角色扮演 - 女声
            "ICL_uranus_zh_female_aojiaonvyou_tob": "傲娇女友 2.0 (豆包同款)",
            "ICL_uranus_zh_female_aomanjiaosheng_tob": "傲慢娇声 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_xiemeinvwang_tob": "邪魅女王 2.0",
            "ICL_uranus_zh_female_bingjiaojiejie_tob": "病娇姐姐 2.0 (豆包同款)",
            "ICL_uranus_zh_female_bingjiaomengmei_tob": "病娇萌妹 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_bingruoshaonv_tob": "病弱少女 2.0",
            "ICL_uranus_zh_female_chengshuwenrou_tob": "成熟温柔 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_chengshujiejie_tob": "成熟姐姐 2.0 (豆包同款)",
            "ICL_uranus_zh_female_chunzhenshaonv_tob": "纯真少女 2.0 (豆包同款)",
            "ICL_uranus_zh_female_chunchenvsheng_tob": "纯澈女生 2.0",
            "ICL_uranus_zh_female_wumeikeren_tob": "妩媚可人 2.0",
            "ICL_uranus_zh_female_guaiqiaokeer_tob": "乖巧可儿 2.0",
            "ICL_uranus_zh_female_heainainai_tob": "和蔼奶奶 2.0",
            "ICL_uranus_zh_female_huopodiaoman_tob": "活泼刁蛮 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_huoponvhai_tob": "活泼女孩 2.0",
            "ICL_uranus_zh_female_jiaohannvwang_tob": "娇憨女王 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_jiaoruoluoli_tob": "娇弱萝莉 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_jiaxiaozi_tob": "假小子 2.0 (豆包同款)",
            "ICL_uranus_zh_female_jinglingxiangdao_tob": "精灵向导 2.0 (豆包同款)",
            "ICL_uranus_zh_female_kailangtingting_tob": "开朗婷婷 2.0",
            "ICL_uranus_zh_female_kaixinxiaohong_tob": "开心小鸿 2.0",
            "ICL_uranus_zh_female_keainvsheng_tob": "可爱女生 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_lingdongxinxin_tob": "灵动欣欣 2.0",
            "ICL_uranus_zh_female_linjuayi_tob": "邻居阿姨 2.0",
            "ICL_uranus_zh_female_tianmeijiaoqiao_tob": "甜美娇俏 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_qinglenggaoya_tob": "清冷高雅 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_lixingyuanzi_tob": "理性圆子 2.0",
            "ICL_uranus_zh_female_xingganmeihuo_tob": "性感魅惑 2.0",
            "ICL_uranus_zh_female_nuanxinqianqian_tob": "暖心茜茜 2.0",
            "ICL_uranus_zh_female_nuanxinxuejie_tob": "暖心学姐 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_qingtianmeimei_tob": "清甜莓莓 2.0",
            "ICL_uranus_zh_female_qingtiantaotao_tob": "清甜桃桃 2.0",
            "ICL_uranus_zh_female_qingxixiaoxue_tob": "清晰小雪 2.0",
            "ICL_uranus_zh_female_qingxinshaonv_tob": "倾心少女 2.0",
            "ICL_uranus_zh_female_rouguhunshi_tob": "柔骨魂师 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_ruanmengtangtang_tob": "软萌糖糖 2.0",
            "ICL_uranus_zh_female_ruanmengtuanzi_tob": "软萌团子 2.0",
            "ICL_uranus_zh_female_tianmeihuopo_tob": "甜美活泼 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_tianmeixiaoju_tob": "甜美小橘 2.0",
            "ICL_uranus_zh_female_tianmeixiaoyu_tob": "甜美小雨 2.0",
            "ICL_uranus_zh_female_tiaopigongzhu_tob": "调皮公主 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_tiexinnvyou_tob": "贴心女友 2.0 (豆包同款)",
            "ICL_uranus_zh_female_wenrounvshen_tob": "温柔女神 2.0 (豆包同款)",
            "ICL_uranus_zh_female_wenrouwenya_tob": "温柔文雅 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_zhixinjiejie_tob": "知心姐姐 2.0",
            "ICL_uranus_zh_female_wumeiyujie_tob": "妩媚御姐 2.0 (豆包同款)",
            "ICL_uranus_zh_female_yuanqitianmei_tob": "元气甜妹 2.0",
            "ICL_uranus_zh_female_xiemeiyujie_tob": "邪魅御姐 2.0",
            "ICL_uranus_zh_female_xingganyujie_tob": "性感御姐 2.0 (豆包同款)",
            "ICL_uranus_zh_female_xiuliqianqian_tob": "秀丽倩倩 2.0",
            "ICL_uranus_zh_female_tiexinguimi_tob": "贴心闺蜜 2.0",
            "ICL_uranus_zh_female_tiexinmeimei_tob": "贴心妹妹 2.0",
            "ICL_uranus_zh_female_wenroubaiyueguang_tob": "温柔白月光 2.0",
            "ICL_uranus_zh_female_chuliannvyou_tob": "初恋女友 2.0",
            "ICL_uranus_zh_female_zhixingwenwan_tob": "知性温婉 2.0 (猫箱同款)",
            "ICL_uranus_zh_female_wenwanshanshan_tob": "温婉珊珊 2.0",
            "ICL_uranus_zh_female_reqingaina_tob": "热情艾娜 2.0",
            "ICL_uranus_zh_female_qingyingduoduo_tob": "轻盈朵朵 2.0",
            # ICL 角色扮演 - 男声
            "ICL_uranus_zh_male_aoqilingren_tob": "傲气凌人 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_anrenqinzhu_tob": "黯刃秦主 2.0 (豆包同款)",
            "ICL_uranus_zh_male_aojiaogongzi_tob": "傲娇公子 2.0",
            "ICL_uranus_zh_male_aojiaojingying_tob": "傲娇精英 2.0",
            "ICL_uranus_zh_male_aomanqingnian_tob": "傲慢青年 2.0",
            "ICL_uranus_zh_male_aomanshaoye_tob": "傲慢少爷 2.0 (豆包同款)",
            "ICL_uranus_zh_male_zhenbiandiyu_tob": "枕边低语 2.0 (抖音同款)",
            "ICL_uranus_zh_male_badaoshaoye_tob": "霸道少爷 2.0",
            "ICL_uranus_zh_male_badaozongcai_tob": "霸道总裁 2.0",
            "ICL_uranus_zh_male_bingjiaobailian_tob": "病娇白莲 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_bingjiaodidi_tob": "病娇弟弟 2.0 (豆包同款)",
            "ICL_uranus_zh_male_bingjiaogege_tob": "病娇哥哥 2.0 (豆包同款)",
            "ICL_uranus_zh_male_bingjiaonanyou_tob": "病娇男友 2.0",
            "ICL_uranus_zh_male_bingjiaoshaonian_tob": "病娇少年 2.0",
            "ICL_uranus_zh_male_bingruogongzi_tob": "病弱公子 2.0 (豆包同款)",
            "ICL_uranus_zh_male_bingruoshaonian_tob": "病弱少年 2.0",
            "ICL_uranus_zh_male_bujiqingnian_tob": "不羁青年 2.0",
            "ICL_uranus_zh_male_chunhoudiyin_tob": "醇厚低音 2.0",
            "ICL_uranus_zh_male_paoxiaoxiaoge_tob": "咆哮小哥 2.0",
            "ICL_uranus_zh_male_yangyang_tob": "炀炀 2.0",
            "ICL_uranus_zh_male_chanruoshaoye_tob": "孱弱少爷 2.0",
            "ICL_uranus_zh_male_chengshuzongcai_tob": "成熟总裁 2.0",
            "ICL_uranus_zh_male_chenwenmingzai_tob": "沉稳明仔 2.0",
            "ICL_uranus_zh_male_qingyisugan_tob": "清逸苏感 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_chunzhenxuedi_tob": "纯真学弟 2.0 (豆包同款)",
            "ICL_uranus_zh_male_cixingnansang_tob": "磁性男嗓 2.0",
            "ICL_uranus_zh_male_cujingnansheng_tob": "醋精男生 2.0",
            "ICL_uranus_zh_male_cujingnanyou_tob": "醋精男友 2.0",
            "ICL_uranus_zh_male_diyinchenyu_tob": "低音沉郁 2.0",
            "ICL_uranus_zh_male_fengfashaonian_tob": "风发少年 2.0",
            "ICL_uranus_zh_male_ruyagongzi_tob": "儒雅公子 2.0",
            "ICL_uranus_zh_male_fuheigongzi_tob": "腹黑公子 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_ganjingshaonian_tob": "干净少年 2.0",
            "ICL_uranus_zh_male_gaolengzongcai_tob": "高冷总裁 2.0",
            "ICL_uranus_zh_male_guaogongzi_tob": "孤傲公子 2.0 (豆包同款)",
            "ICL_uranus_zh_male_gugaogongzi_tob": "孤高公子 2.0",
            "ICL_uranus_zh_male_guiyishenmi_tob": "诡异神秘 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_guzhibingjiao_tob": "固执病娇 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_hanhoudunshi_tob": "憨厚敦实 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_huoliqingnian_tob": "活力青年 2.0",
            "ICL_uranus_zh_male_huoponanyou_tob": "活泼男友 2.0",
            "ICL_uranus_zh_male_huoposhuanglang_tob": "活泼爽朗 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_huzishushu_tob": "胡子叔叔 2.0",
            "ICL_uranus_zh_male_jijiazhineng_tob": "机甲智能 2.0",
            "ICL_uranus_zh_male_jingyingqingnian_tob": "精英青年 2.0",
            "ICL_uranus_zh_male_junyigongzi_tob": "俊逸公子 2.0",
            "ICL_uranus_zh_male_kailangqingkuai_tob": "开朗轻快 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_kailangqingnian_tob": "开朗青年 2.0",
            "ICL_uranus_zh_male_lanyincaohunshi_tob": "蓝银草魂师 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_lengaozongcai_tob": "冷傲总裁 2.0",
            "ICL_uranus_zh_male_lengdanshuli_tob": "冷淡疏离 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_lengjungaozhi_tob": "冷峻高智 2.0",
            "ICL_uranus_zh_male_lengjunshangsi_tob": "冷峻上司 2.0 (豆包同款)",
            "ICL_uranus_zh_male_lengkugege_tob": "冷酷哥哥 2.0 (豆包同款)",
            "ICL_uranus_zh_male_lenglianxiongzhang_tob": "冷脸兄长 2.0",
            "ICL_uranus_zh_male_lenglianxueba_tob": "冷脸学霸 2.0",
            "ICL_uranus_zh_male_lengmonanyou_tob": "冷漠男友 2.0",
            "ICL_uranus_zh_male_lengmoxiongzhang_tob": "冷漠兄长 2.0",
            "ICL_uranus_zh_male_lingyunqingnian_tob": "凌云青年 2.0",
            "ICL_uranus_zh_male_qinglengjingui_tob": "清冷矜贵 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_lvchaxiaoge_tob": "绿茶小哥 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_mengdongqingnian_tob": "懵懂青年 2.0",
            "ICL_uranus_zh_male_menyoupingxiaoge_tob": "闷油瓶小哥 2.0 (豆包同款)",
            "ICL_uranus_zh_male_xiaozhangxiaoge_tob": "嚣张小哥 2.0",
            "ICL_uranus_zh_male_nianrennanyou_tob": "粘人男友 2.0",
            "ICL_uranus_zh_male_neiliancaijun_tob": "内敛才俊 2.0",
            "ICL_uranus_zh_male_nuanxintitie_tob": "暖心体贴 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_pianpiangongzi_tob": "翩翩公子 2.0",
            "ICL_uranus_zh_male_chenwenyouya_tob": "沉稳优雅 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_qingsexiaosheng_tob": "青涩小生 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_qingseqingnian_tob": "青涩青年 2.0",
            "ICL_uranus_zh_male_qingshuangshaonian_tob": "清爽少年 2.0",
            "ICL_uranus_zh_male_qingxinbobo_tob": "清新波波 2.0",
            "ICL_uranus_zh_male_qinqieqingnian_tob": "亲切青年 2.0",
            "ICL_uranus_zh_male_qinqiexiaozhuo_tob": "亲切小卓 2.0",
            "ICL_uranus_zh_male_qinglangwenrun_tob": "清朗温润 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_rexueshaonian_tob": "热血少年 2.0",
            "ICL_uranus_zh_male_ruyacaijun_tob": "儒雅才俊 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_ruyajunzi_tob": "儒雅君子 2.0",
            "ICL_uranus_zh_male_ruyazongcai_tob": "儒雅总裁 2.0",
            "ICL_uranus_zh_male_sajiaonansheng_tob": "撒娇男生 2.0",
            "ICL_uranus_zh_male_sajiaonanyou_tob": "撒娇男友 2.0",
            "ICL_uranus_zh_male_sajiaonianren_tob": "撒娇粘人 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_satuoqingnian_tob": "洒脱青年 2.0",
            "ICL_uranus_zh_male_shaonianjiangjun_tob": "少年将军 2.0 (豆包同款)",
            "ICL_uranus_zh_male_shenchenzongcai_tob": "深沉总裁 2.0",
            "ICL_uranus_zh_male_jilingxiaohuo_tob": "机灵小伙 2.0",
            "ICL_uranus_zh_male_shenmifashi_tob": "神秘法师 2.0 (豆包同款)",
            "ICL_uranus_zh_male_shuaizhenxiaohuo_tob": "率真小伙 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_shuanglangxiaoyang_tob": "爽朗小阳 2.0",
            "ICL_uranus_zh_male_dichenqianquan_tob": "低沉缱绻 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_siwenqingnian_tob": "斯文青年 2.0",
            "ICL_uranus_zh_male_tianxinanyou_tob": "甜系男友 2.0",
            "ICL_uranus_zh_male_tiexinnanyou_tob": "贴心男友 2.0 (豆包同款)",
            "ICL_uranus_zh_male_wenrounantongzhuo_tob": "温柔男同桌 2.0 (豆包同款)",
            "ICL_uranus_zh_male_wenrounanyou_tob": "温柔男友 2.0",
            "ICL_uranus_zh_male_wenrouxuezhang_tob": "温柔学长 2.0",
            "ICL_uranus_zh_male_wenrunxuezhe_tob": "温润学者 2.0",
            "ICL_uranus_zh_male_wenshunshaonian_tob": "温顺少年 2.0",
            "ICL_uranus_zh_male_guayanxiaoge_tob": "寡言小哥 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_xiaohouye_tob": "小侯爷 2.0",
            "ICL_uranus_zh_male_naiqixiaosheng_tob": "奶气小生 2.0 (豆包同款)",
            "ICL_uranus_zh_male_xiaosasuixing_tob": "潇洒随性 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_wenrouneilian_tob": "温柔内敛 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_xuebanantongzhuo_tob": "学霸男同桌 2.0 (豆包同款)",
            "ICL_uranus_zh_male_xuebatongzhuo_tob": "学霸同桌 2.0",
            "ICL_uranus_zh_male_yangguangyangyang_tob": "阳光洋洋 2.0",
            "ICL_uranus_zh_male_wennuanshaonian_tob": "温暖少年 2.0",
            "ICL_uranus_zh_male_yiqishaonian_tob": "意气少年 2.0",
            "ICL_uranus_zh_male_younidashu_tob": "油腻大叔 2.0",
            "ICL_uranus_zh_male_youmodaye_tob": "幽默大爷 2.0 (豆包同款)",
            "ICL_uranus_zh_male_youmoshushu_tob": "幽默叔叔 2.0 (豆包同款)",
            "ICL_uranus_zh_male_youroubangzhu_tob": "优柔帮主 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_yourougongzi_tob": "优柔公子 2.0 (豆包同款)",
            "ICL_uranus_zh_male_yuanqishaonian_tob": "元气少年 2.0",
            "ICL_uranus_zh_male_zhangjianjunzi_tob": "仗剑君子 2.0",
            "ICL_uranus_zh_male_zhangjianxiake_tob": "仗剑侠客 2.0",
            "ICL_uranus_zh_male_zhengzhiqingnian_tob": "正直青年 2.0 (猫箱同款)",
            "ICL_uranus_zh_male_zhishuaiqingnian_tob": "直率青年 2.0",
            "ICL_uranus_zh_male_zhongerqingnian_tob": "中二青年 2.0",
            "ICL_uranus_zh_male_zifuqingnian_tob": "自负青年 2.0",
            "ICL_uranus_zh_male_zixinqingnian_tob": "自信青年 2.0",
            "ICL_uranus_zh_male_tiancaitongzhuo_tob": "天才同桌 2.0",
            "ICL_uranus_zh_male_qingxinmumu_tob": "清新沐沐 2.0",
            "ICL_uranus_zh_male_shuanglangshaonian_tob": "爽朗少年 2.0"
        }

    saved_voice_type = config.doubaotts.get("speaker", "zh_female_vv_uranus_bigtts")
    if saved_voice_type not in voice_options:
        voice_options[saved_voice_type] = f"{tr('Custom Voice')} ({saved_voice_type})"

    selected_voice_display = st.selectbox(
        tr("Voice Selection"),
        options=list(voice_options.values()),
        index=list(voice_options.keys()).index(saved_voice_type) if saved_voice_type in voice_options else 0,
        help=tr("Select Doubao TTS Voice")
    )

    # 获取实际的音色 ID
    voice_type = list(voice_options.keys())[
        list(voice_options.values()).index(selected_voice_display)
    ]

    # 音频格式选择
    audio_format_options = {
        "pcm": "PCM (推荐用于流式)",
        "mp3": "MP3",
        "ogg_opus": "OGG Opus",
        "wav": "WAV"
    }
    saved_audio_format = config.doubaotts.get("audio_format", "mp3")
    if saved_audio_format not in audio_format_options:
        saved_audio_format = "pcm"

    audio_format = st.selectbox(
        tr("Audio Format"),
        options=list(audio_format_options.keys()),
        format_func=lambda x: audio_format_options[x],
        index=list(audio_format_options.keys()).index(saved_audio_format),
        help=tr("Doubao Audio Format Help")
    )

    # 高级参数折叠面板
    with st.expander(tr("Advanced Parameters"), expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            # 语速调节
            voice_rate = st.slider(
                tr("Voice Rate"),
                min_value=0.5,
                max_value=2.0,
                value=config.ui.get("doubaotts_rate", 1.0),
                step=0.1,
                help=tr("Voice Rate Help 0.5-2.0")
            )

            # 音量调节
            voice_volume = st.slider(
                tr("Voice Volume"),
                min_value=0.1,
                max_value=2.0,
                value=config.doubaotts.get("volume", 1.0),
                step=0.1,
                help=tr("Voice Volume Help 0.1-2.0")
            )

        with col2:
            # 音高调节
            voice_pitch = st.slider(
                tr("Voice Pitch"),
                min_value=0.5,
                max_value=1.5,
                value=config.doubaotts.get("pitch", 1.0),
                step=0.1,
                help=tr("Voice Pitch Help 0.5-1.5")
            )

            # 句尾静音时长
            silence_duration_value = config.doubaotts.get("silence_duration", 0.0)
            # 确保类型一致（转换为 float）
            silence_duration_value = float(silence_duration_value) if silence_duration_value is not None else 0.0

            silence_duration = st.slider(
                tr("Sentence Silence Duration"),
                min_value=0.0,
                max_value=30.0,
                value=silence_duration_value,
                step=0.5,
                help=tr("Sentence Silence Duration Help")
            )

        # 可选功能
        st.subheader(tr("Optional Features"))
        disable_markdown_filter = st.checkbox(
            tr("Disable Markdown Filter"),
            value=config.doubaotts.get("disable_markdown_filter", False),
            help=tr("Disable Markdown Filter Help")
        )
        disable_emoji_filter = st.checkbox(
            tr("Disable Emoji Filter"),
            value=config.doubaotts.get("disable_emoji_filter", False),
            help=tr("Disable Emoji Filter Help")
        )
        enable_latex_tn = st.checkbox(
            tr("Enable Latex TN"),
            value=config.doubaotts.get("enable_latex_tn", False),
            help=tr("Enable Latex TN Help")
        )
        require_usage_tokens_return = st.checkbox(
            tr("Require Usage Tokens Return"),
            value=config.doubaotts.get("require_usage_tokens_return", False),
            help=tr("Require Usage Tokens Return Help")
        )

    # 显示 API Key 申请流程
    with st.expander(tr("Doubao TTS API Key Application Process"), expanded=False):
        st.write(f"**{tr('Application Steps')}:**")
        st.write("1. " + tr("Doubao TTS Step 1: Open Volcengine Console"))
        st.write("2. " + tr("Doubao TTS Step 2: Create API Key"))
        st.write("3. " + tr("Doubao TTS Step 3: Access Voice Synthesis Service"))
        st.write("4. " + tr("Doubao TTS Step 4: Get Speaker ID from Console"))
        st.write("5. " + tr("Doubao TTS Step 5: Fill in API Key and Resource ID"))
        st.write("6. " + tr("Doubao TTS Step 6: Test and Use"))

        st.write("")
        st.info(tr("Doubao TTS Fill Credentials Notice"))

    # 保存配置
    config.doubaotts["api_key"] = api_key
    config.doubaotts["resource_id"] = resource_id
    config.doubaotts["speaker"] = voice_type
    config.doubaotts["audio_format"] = audio_format
    config.doubaotts["volume"] = voice_volume
    config.doubaotts["pitch"] = voice_pitch
    config.doubaotts["silence_duration"] = silence_duration
    config.doubaotts["disable_markdown_filter"] = disable_markdown_filter
    config.doubaotts["disable_emoji_filter"] = disable_emoji_filter
    config.doubaotts["enable_latex_tn"] = enable_latex_tn
    config.doubaotts["require_usage_tokens_return"] = require_usage_tokens_return
    config.ui["doubaotts_voice_type"] = voice_type
    config.ui["doubaotts_rate"] = voice_rate
    config.ui["voice_name"] = voice_type  # 兼容性
    st.session_state['voice_rate'] = voice_rate

    # 显示配置状态
    if api_key:
        st.success(tr("Doubao TTS 2.0 configured"))
    else:
        st.warning(tr("Please configure API Key"))



def render_voice_preview_new(tr, selected_engine):
    """渲染新的语音试听功能"""
    if st.button(tr("Preview Voice Synthesis"), use_container_width=True):
        play_content = tr("Voice Preview Sample")

        # 根据选择的引擎获取对应的语音配置
        voice_name = ""
        voice_rate = 1.0
        voice_pitch = 1.0

        if selected_engine == "edge_tts":
            voice_name = config.ui.get("edge_voice_name", "zh-CN-XiaoyiNeural-Female")
            voice_rate = config.ui.get("edge_rate", 1.0)
            voice_pitch = 1.0 + (config.ui.get("edge_pitch", 0) / 100.0)
        elif selected_engine == "azure_speech":
            voice_name = config.ui.get("azure_voice_name", "zh-CN-XiaoxiaoMultilingualNeural")
            voice_rate = config.ui.get("azure_rate", 1.0)
            voice_pitch = 1.0 + (config.ui.get("azure_pitch", 0) / 100.0)
        elif selected_engine == "soulvoice":
            voice_uri = config.soulvoice.get("voice_uri", "")
            if voice_uri:
                if not voice_uri.startswith("soulvoice:") and not voice_uri.startswith("speech:"):
                    voice_name = f"soulvoice:{voice_uri}"
                else:
                    voice_name = voice_uri if voice_uri.startswith("soulvoice:") else f"soulvoice:{voice_uri}"
            voice_rate = 1.0  # SoulVoice 使用默认语速
            voice_pitch = 1.0  # SoulVoice 不支持音调调节
        elif selected_engine == "tencent_tts":
            voice_type = config.ui.get("tencent_voice_type", "101001")
            voice_name = f"tencent:{voice_type}"
            voice_rate = config.ui.get("tencent_rate", 1.0)
            voice_pitch = 1.0  # 腾讯云 TTS 不支持音调调节
        elif selected_engine == "qwen3_tts":
            vt = config.ui.get("qwen_voice_type", "Cherry")
            voice_name = f"qwen3:{vt}"
            voice_rate = config.ui.get("qwen3_rate", 1.0)
            voice_pitch = 1.0  # Qwen3 TTS 不支持音调调节
        elif selected_engine == config.INDEXTTS_ENGINE:
            reference_audio = config.indextts.get("reference_audio", "")
            if reference_audio:
                voice_name = f"{config.INDEXTTS_VOICE_PREFIX}{reference_audio}"
            voice_rate = 1.0  # IndexTTS-1.5 不支持速度调节
            voice_pitch = 1.0  # IndexTTS-1.5 不支持音调调节
        elif selected_engine == config.INDEXTTS2_ENGINE:
            reference_audio = config.indextts2.get("reference_audio", "")
            if reference_audio:
                voice_name = f"{config.INDEXTTS2_VOICE_PREFIX}{reference_audio}"
            voice_rate = 1.0  # IndexTTS-2 使用自身生成参数
            voice_pitch = 1.0
        elif selected_engine == config.OMNIVOICE_ENGINE:
            mode = config.omnivoice.get("mode", "auto")
            reference_audio = config.omnivoice.get("reference_audio", "")
            if mode == "voice_clone" and reference_audio:
                voice_name = f"{config.OMNIVOICE_VOICE_PREFIX}{reference_audio}"
            else:
                voice_name = f"{config.OMNIVOICE_VOICE_PREFIX}{mode}"
            voice_rate = config.omnivoice.get("speed", 1.0)
            voice_pitch = 1.0
        elif selected_engine == "doubaotts":
            voice_type = config.ui.get("doubaotts_voice_type", "zh_female_vv_uranus_bigtts")
            voice_name = voice_type
            voice_rate = config.ui.get("doubaotts_rate", 1.0)
            voice_pitch = 1.0  # 豆包语音 TTS 不支持音调调节

        if not voice_name:
            st.error(tr("Please configure voice settings first"))
            return

        with st.spinner(tr("Synthesizing Voice")):
            temp_dir = utils.storage_dir("temp", create=True)
            audio_format = "audio/wav" if selected_engine in (
                config.INDEXTTS_ENGINE,
                config.INDEXTTS2_ENGINE,
                config.OMNIVOICE_ENGINE,
            ) else "audio/mp3"
            audio_extension = ".wav" if audio_format == "audio/wav" else ".mp3"
            audio_file = os.path.join(temp_dir, f"tmp-voice-{str(uuid4())}{audio_extension}")

            sub_maker = voice.tts(
                text=play_content,
                voice_name=voice_name,
                voice_rate=voice_rate,
                voice_pitch=voice_pitch,
                voice_file=audio_file,
                tts_engine=st.session_state.get('tts_engine')
            )

            if sub_maker and os.path.exists(audio_file):
                st.success(tr("Voice synthesis successful"))

                # 播放音频
                with open(audio_file, 'rb') as audio_file_obj:
                    audio_bytes = audio_file_obj.read()
                    st.audio(audio_bytes, format=audio_format)

                # 清理临时文件
                try:
                    os.remove(audio_file)
                except:
                    pass
            else:
                st.error(tr("Voice synthesis failed"))


def render_azure_v2_settings(tr):
    """渲染Azure V2语音设置（保留兼容性）"""
    saved_azure_speech_region = config.azure.get("speech_region", "")
    saved_azure_speech_key = config.azure.get("speech_key", "")

    azure_speech_region = st.text_input(
        tr("Speech Region"),
        value=saved_azure_speech_region
    )
    azure_speech_key = st.text_input(
        tr("Speech Key"),
        value=saved_azure_speech_key,
        type="password"
    )

    config.azure["speech_region"] = azure_speech_region
    config.azure["speech_key"] = azure_speech_key


def render_voice_parameters(tr, voice_name):
    """渲染语音参数设置（保留兼容性）"""
    # 音量 - 使用统一的默认值
    voice_volume = st.slider(
        tr("Speech Volume"),
        min_value=AudioVolumeDefaults.MIN_VOLUME,
        max_value=AudioVolumeDefaults.MAX_VOLUME,
        value=AudioVolumeDefaults.VOICE_VOLUME,
        step=0.01,
        help=tr("Adjust the volume of the original audio")
    )
    st.session_state['voice_volume'] = voice_volume

    # 检查是否为 SoulVoice 引擎
    is_soulvoice = voice.is_soulvoice_voice(voice_name)

    # 语速
    if is_soulvoice:
        # SoulVoice 支持更精细的语速控制
        voice_rate = st.slider(
            tr("Speech Rate"),
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="SoulVoice 语音速度控制"
        )
    else:
        # Azure TTS 使用预设选项
        voice_rate = st.selectbox(
            tr("Speech Rate"),
            options=[0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5, 1.8, 2.0],
            index=2,
        )
    st.session_state['voice_rate'] = voice_rate

    # 音调 - SoulVoice 不支持音调调节
    if not is_soulvoice:
        voice_pitch = st.selectbox(
            tr("Speech Pitch"),
            options=[0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5, 1.8, 2.0],
            index=2,
        )
        st.session_state['voice_pitch'] = voice_pitch
    else:
        # SoulVoice 不支持音调调节，设置默认值
        st.session_state['voice_pitch'] = 1.0
        st.info(tr("SoulVoice pitch not supported"))


def render_voice_preview(tr, voice_name):
    """渲染语音试听功能"""
    if st.button(tr("Play Voice")):
        play_content = "感谢关注 NarratoAI，有任何问题或建议，可以关注微信公众号，求助或讨论"
        if not play_content:
            play_content = st.session_state.get('video_script', '')
        if not play_content:
            play_content = tr("Voice Example")

        with st.spinner(tr("Synthesizing Voice")):
            temp_dir = utils.storage_dir("temp", create=True)
            audio_file = os.path.join(temp_dir, f"tmp-voice-{str(uuid4())}.mp3")

            sub_maker = voice.tts(
                text=play_content,
                voice_name=voice_name,
                voice_rate=st.session_state.get('voice_rate', 1.0),
                voice_pitch=st.session_state.get('voice_pitch', 1.0),
                voice_file=audio_file,
            )

            # 如果语音文件生成失败，使用默认内容重试
            if not sub_maker:
                play_content = "This is a example voice. if you hear this, the voice synthesis failed with the original content."
                sub_maker = voice.tts(
                    text=play_content,
                    voice_name=voice_name,
                    voice_rate=st.session_state.get('voice_rate', 1.0),
                    voice_pitch=st.session_state.get('voice_pitch', 1.0),
                    voice_file=audio_file,
                )

            if sub_maker and os.path.exists(audio_file):
                st.success(tr("Voice synthesis successful"))
                st.audio(audio_file, format="audio/mp3")
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            else:
                st.error(tr("Voice synthesis failed"))


def render_bgm_settings(tr):
    """渲染背景音乐设置"""
    saved_bgm_file = st.session_state.get('bgm_file', '')
    saved_bgm_source = st.session_state.get('bgm_source', 'resource')
    if st.session_state.get('bgm_type') == "":
        saved_bgm_source = "none"

    bgm_source_options = {
        tr("Select from Resource Directory"): "resource",
        tr("Upload Background Music"): "upload",
        tr("No Background Music"): "none",
    }
    if saved_bgm_source not in bgm_source_options.values():
        saved_bgm_source = "resource"

    default_bgm_source_label = next(
        label
        for label, source_value in bgm_source_options.items()
        if source_value == saved_bgm_source
    )

    st.markdown(f"**{tr('Background Music')}**")
    bgm_source_label = st.pills(
        tr("Background Music Source"),
        options=list(bgm_source_options.keys()),
        selection_mode="single",
        default=default_bgm_source_label,
        key="bgm_source_selection",
        help=tr("Background Music Source Help"),
        label_visibility="collapsed",
        width="stretch",
    )
    if not bgm_source_label:
        bgm_source_label = default_bgm_source_label

    bgm_source = bgm_source_options[bgm_source_label]
    bgm_file = ""
    bgm_name = ""

    if bgm_source == "resource":
        bgm_options = get_bgm_resource_options()
        if bgm_options:
            selected_bgm_index = get_bgm_resource_index(bgm_options, saved_bgm_file)
            select_col, preview_col = st.columns([5, 1])
            with select_col:
                selected_bgm_option = bgm_options[st.selectbox(
                    tr("Background Music"),
                    options=range(len(bgm_options)),
                    index=selected_bgm_index,
                    format_func=lambda x: format_bgm_resource_option(bgm_options[x]),
                    help=tr("Background Music Path Help"),
                    label_visibility="collapsed"
                )]
            bgm_file = selected_bgm_option["path"]
            bgm_name = selected_bgm_option["title"]
            with preview_col:
                render_bgm_preview_button(
                    bgm_file,
                    "resource_bgm_preview",
                    tr,
                )
        else:
            st.warning(tr("No Background Music Resources Found"))

    if bgm_source == "upload":
        if st.session_state.get('bgm_source') != "upload":
            saved_bgm_file = ""
        bgm_file = saved_bgm_file if saved_bgm_file and os.path.isfile(saved_bgm_file) else ""
        bgm_name = os.path.splitext(os.path.basename(bgm_file))[0] if bgm_file else ""
        upload_col, preview_col = st.columns([5, 1])
        with upload_col:
            uploaded_file = st.file_uploader(
                tr("Upload Background Music File"),
                type=[extension.lstrip(".") for extension in BGM_AUDIO_EXTENSIONS],
                help=tr("Upload Background Music Help"),
                label_visibility="collapsed"
            )

        if uploaded_file is not None:
            target_dir = utils.storage_dir(BGM_UPLOAD_SUBDIR, create=True)
            bgm_file = os.path.join(target_dir, f"uploaded_{uploaded_file.name}")
            with open(bgm_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            bgm_name = os.path.splitext(uploaded_file.name)[0]
            st.success(tr("Background Music uploaded").format(path=bgm_file))
        with preview_col:
            render_bgm_preview_button(
                bgm_file,
                "upload_bgm_preview",
                tr,
            )

    preview_bgm_path = st.session_state.get("bgm_preview_path", "")
    if preview_bgm_path == bgm_file and os.path.isfile(preview_bgm_path):
        with open(preview_bgm_path, "rb") as audio_file:
            st.audio(audio_file.read(), format=get_audio_mime_type(preview_bgm_path))

    bgm_type = "" if bgm_source == "none" or not bgm_file else "custom"
    st.session_state['bgm_source'] = bgm_source
    st.session_state['bgm_type'] = bgm_type
    st.session_state['bgm_file'] = bgm_file if bgm_type else ""
    st.session_state['bgm_name'] = bgm_name if bgm_type else ""

    # 背景音乐音量 - 使用统一的默认值
    bgm_volume = st.slider(
        tr("Background Music Volume"),
        min_value=AudioVolumeDefaults.MIN_VOLUME,
        max_value=AudioVolumeDefaults.MAX_VOLUME,
        value=AudioVolumeDefaults.BGM_VOLUME,
        step=0.01,
        help=tr("Adjust the volume of the original audio")
    )
    st.session_state['bgm_volume'] = bgm_volume


def get_audio_params():
    """获取音频参数"""
    return {
        'voice_name': config.ui.get("voice_name", ""),
        'voice_volume': st.session_state.get('voice_volume', AudioVolumeDefaults.VOICE_VOLUME),
        'voice_rate': st.session_state.get('voice_rate', 1.0),
        'voice_pitch': st.session_state.get('voice_pitch', 1.0),
        'bgm_name': st.session_state.get('bgm_name', ''),
        'bgm_type': st.session_state.get('bgm_type', 'random'),
        'bgm_file': st.session_state.get('bgm_file', ''),
        'bgm_volume': st.session_state.get('bgm_volume', AudioVolumeDefaults.BGM_VOLUME),
        'tts_engine': st.session_state.get('tts_engine', config.INDEXTTS_ENGINE),
    }
