from enum import IntEnum


class ParameterType(IntEnum):
    bool      = 0,    # agl::utl::Parameter<bool>
    f32       = 1,    # agl::utl::Parameter<f32>
    int       = 2,    # agl::utl::Parameter<s32>
    vec2      = 3,    # agl::utl::Parameter<sead::Vector2f>
    vec3      = 4,    # agl::utl::Parameter<sead::Vector3f>
    vec4      = 5,    # agl::utl::Parameter<sead::Vector4f>
    color     = 6,    # agl::utl::Parameter<sead::Color4f>
    string32  = 7,    # agl::utl::Parameter<sead::FixedSafeString<32>>

    # Unused in NSMBU (except curve1)
    string64  = 8,    # agl::utl::Parameter<sead::FixedSafeString<64>>
    curve1    = 9,    # agl::utl::ParameterCurve1f
    curve2    = 10,   # agl::utl::ParameterCurve2f
    curve3    = 11,   # agl::utl::ParameterCurve3f
    curve4    = 12    # agl::utl::ParameterCurve4f


class CurveType(IntEnum):
    Linear = 0
    Hermit = 1
    Step = 2
    Sin = 3
    Cos = 4
    SinPow2 = 5
    Linear2D = 6
    Hermit2D = 7
    Step2D = 8
    NonuniformSpline = 9
