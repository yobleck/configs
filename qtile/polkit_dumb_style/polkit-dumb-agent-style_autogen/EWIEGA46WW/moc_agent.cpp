/****************************************************************************
** Meta object code from reading C++ file 'agent.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../agent.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#include <QtCore/QList>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'agent.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.2. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_Agent_t {
    QByteArrayData data[13];
    char stringdata0[199];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_Agent_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_Agent_t qt_meta_stringdata_Agent = {
    {
QT_MOC_LITERAL(0, 0, 5), // "Agent"
QT_MOC_LITERAL(1, 6, 15), // "D-Bus Interface"
QT_MOC_LITERAL(2, 22, 46), // "org.freedesktop.PolicyKit1.Au..."
QT_MOC_LITERAL(3, 69, 19), // "BeginAuthentication"
QT_MOC_LITERAL(4, 89, 0), // ""
QT_MOC_LITERAL(5, 90, 8), // "actionId"
QT_MOC_LITERAL(6, 99, 7), // "message"
QT_MOC_LITERAL(7, 107, 8), // "iconName"
QT_MOC_LITERAL(8, 116, 21), // "QMap<QString,QString>"
QT_MOC_LITERAL(9, 138, 7), // "details"
QT_MOC_LITERAL(10, 146, 6), // "cookie"
QT_MOC_LITERAL(11, 153, 34), // "QList<QPair<QString,QVariantM..."
QT_MOC_LITERAL(12, 188, 10) // "identities"

    },
    "Agent\0D-Bus Interface\0"
    "org.freedesktop.PolicyKit1.AuthenticationAgent\0"
    "BeginAuthentication\0\0actionId\0message\0"
    "iconName\0QMap<QString,QString>\0details\0"
    "cookie\0QList<QPair<QString,QVariantMap> >\0"
    "identities"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_Agent[] = {

 // content:
       8,       // revision
       0,       // classname
       1,   14, // classinfo
       1,   16, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // classinfo: key, value
       1,    2,

 // slots: name, argc, parameters, tag, flags
       3,    6,   21,    4, 0x4a /* Public | isScriptable */,

 // slots: parameters
    QMetaType::Void, QMetaType::QString, QMetaType::QString, QMetaType::QString, 0x80000000 | 8, QMetaType::QString, 0x80000000 | 11,    5,    6,    7,    9,   10,   12,

       0        // eod
};

void Agent::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<Agent *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
        case 0: _t->BeginAuthentication((*reinterpret_cast< const QString(*)>(_a[1])),(*reinterpret_cast< const QString(*)>(_a[2])),(*reinterpret_cast< const QString(*)>(_a[3])),(*reinterpret_cast< const QMap<QString,QString>(*)>(_a[4])),(*reinterpret_cast< const QString(*)>(_a[5])),(*reinterpret_cast< const QList<QPair<QString,QVariantMap> >(*)>(_a[6]))); break;
        default: ;
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject Agent::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_meta_stringdata_Agent.data,
    qt_meta_data_Agent,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *Agent::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *Agent::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_Agent.stringdata0))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int Agent::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 1)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 1;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 1)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 1;
    }
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
