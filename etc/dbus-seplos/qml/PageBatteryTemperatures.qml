import QtQuick 1.1
import com.victron.velib 1.0
import "utils.js" as Utils

MbPage {
    id: root
	property string bindPrefix

    title: service.description + " | Cell Temperatures"
    model: VisibleItemModel {
        MbItemValue {
            description: qsTr("Box temperature")
            show: item.valid
            item {
                bind: service.path("/Dc/0/Temperature")
                displayUnit: user.temperatureUnit
            }
        }
        MbItemValue {
            description: qsTr("MOSFET temperature")
            show: item.valid
            item {
                bind: service.path("/System/MOSFET_Temperature")
                displayUnit: user.temperatureUnit
            }
        }
		MbItemValue {
			description: qsTr("Temperature 1")
			item {
				bind: Utils.path(root.bindPrefix, "/System/Temperature1")
			}
		}
		MbItemValue {
			description: qsTr("Temperature 2")
			item {
				bind: Utils.path(root.bindPrefix, "/System/Temperature2")
			}
		}
		MbItemValue {
			description: qsTr("Temperature 3")
			item {
				bind: Utils.path(root.bindPrefix, "/System/Temperature3")
			}
		}
		MbItemValue {
			description: qsTr("Temperature 4")
			item {
				bind: Utils.path(root.bindPrefix, "/System/Temperature4")
			}
		}
    }
}