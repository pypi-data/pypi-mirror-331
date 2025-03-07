from imxIcons.domain.supportedImxVersions import ImxVersionEnum
from imxIcons.iconEntity import IconEntity, IconSvgGroup

entities_path = "SpeedSign"
imx_version = ImxVersionEnum.v124


def add_arrow_marker(sign):
    temp_list = []
    for item in sign:
        translate = "translate(-4, -1.15)"
        temp_list.append(
            item.extend_icon(
                name=item.icon_name + "ArrowRight",
                extra_props={"hasArrowMarker": "True"},
                extra_groups=[IconSvgGroup("arrow-sign", f"rotate(180), {translate}")],
            )
        )
        temp_list.append(
            item.extend_icon(
                name=item.icon_name + "ArrowDouble",
                extra_props={"hasArrowMarker": "True"},
                extra_groups=[
                    IconSvgGroup("arrow-sign-double", f"rotate(180), {translate}")
                ],
                extra_additional_props={"ArrowMarkerDouble": "True"},
            )
        )

    sign.extend(temp_list)


signs = [
    IconEntity(
        imx_version=imx_version,
        imx_path=entities_path,
        icon_name="RS314",
        properties={
            "speedSignType": "MaximumSpeed",
        },
        icon_groups=[
            IconSvgGroup("sign-normal-base"),
            IconSvgGroup("RS-314", "translate(6.5, 0)"),
        ],
    ),
    IconEntity(
        imx_version=imx_version,
        imx_path=entities_path,
        icon_name="RS314Bis",
        properties={
            "speedSignType": "MaximumSpeed",
            "cargoSpeed": "*",
        },
        icon_groups=[
            IconSvgGroup("sign-normal-base"),
            IconSvgGroup("RS-314", "translate(5, 0)"),
            IconSvgGroup("RS-314", "translate(10, 0)"),
        ],
    ),
    IconEntity(
        imx_version=imx_version,
        imx_path=entities_path,
        icon_name="RS313",
        properties={
            "speedSignType": "DecelerateToSpeed",
        },
        icon_groups=[
            IconSvgGroup("sign-normal-base"),
            IconSvgGroup("RS-313", "translate(6.5, 0)"),
        ],
    ),
    IconEntity(
        imx_version=imx_version,
        imx_path=entities_path,
        icon_name="RS313Bis",
        properties={
            "speedSignType": "DecelerateToSpeed",
            "cargoSpeed": "*",
        },
        icon_groups=[
            IconSvgGroup("sign-normal-base"),
            IconSvgGroup("RS-313", "translate(4, 0)"),
            IconSvgGroup("RS-313", "translate(10, 0)"),
        ],
    ),
    IconEntity(
        imx_version=imx_version,
        imx_path=entities_path,
        icon_name="RS316",
        properties={
            "speedSignType": "AccelerateToSpeed",
        },
        icon_groups=[
            IconSvgGroup("sign-normal-base"),
            IconSvgGroup("RS-316", "translate(6.5, 0)"),
        ],
    ),
    # todo
    # snelheid_ovw == LevelCrossingWeighBridgeSpeed == RS 324
    # goe_afrem
]

add_arrow_marker(signs)

signs.sort(key=lambda obj: obj.icon_name)
speed_sign_icon_entities_v124 = signs
