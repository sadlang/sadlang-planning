<div dir="rtl">

# 📐 مخطّطات القلب الموحَّد (RFC #10)

> مخطّطات Mermaid لطبقات الأهداف والحدود المفروضة وتقدّم المراحل. المرجع المعماريّ الكامل: **RFC sadlang-rfcs#10**.

---

## طبقات الأهداف والحدود المفروضة

```mermaid
flowchart TB
    subgraph FOUND["① الأساس المشترك — يربطه المحرّكان"]
        SHARED["sad_shared<br/>معجم · محلّل · AST · أنواع · قيمة · أخطاء<br/><b>+ المصدر المولَّد من SoT</b>"]
        BAND["الحزام المشترك<br/>sad_type_system · sad_semantic(=sad_ownership)<br/>sad_memory_* · sad_security_core · sad_null_safety · sad_mobile"]
    end

    subgraph INTERP["② نظام المفسّر — sad-run فقط"]
        CORE["sad_interp <i>(sad_core = alias توافق)</i>"]
        RT["sad_runtime<br/>(مدراء وقت التشغيل — شقيق الآلة القادمة)"]
        BLT["sad_builtins · sad_lowlevel"]
        UIB["sad_ui_bridge · sad_ui · الشبكة"]
    end

    subgraph COMPILE["③ نظام المترجم — sad-build فقط"]
        COMP["sad_compiler"]
        BACK["sad_frontend · sad_optimizer<br/>sad_llvm_backend · sad_tools"]
    end

    RUN(["apps/sad-run<br/>المفسّر الشجريّ"])
    BUILD(["apps/sad-build<br/>المترجم ⟸ LLVM"])

    CORE --> RT & BLT & UIB
    CORE --> SHARED & BAND
    RUN --> CORE
    COMP --> BACK & BAND
    BUILD --> SHARED & COMP

    GUARD{{"حارسان في CI:<br/>check_layering (G4)<br/>check_interpreter_boundary"}}
    GUARD -. يمنع روابط المحرّكَين المتقاطعة .-> INTERP
    GUARD -. ويمنع رؤية المترجم لترويسات المفسّر .-> COMPILE

    style SHARED fill:#1b5e20,color:#fff
    style FOUND fill:#0d3d12,color:#fff
    style INTERP fill:#3e2723,color:#fff
    style COMPILE fill:#1a237e,color:#fff
    style GUARD fill:#b71c1c,color:#fff
```

---

## تقدّم المراحل

```mermaid
flowchart LR
    M0["م0 ✅<br/>x.py"] --> M1["م1 ✅<br/>SoT + حارس"]
    M1 --> M2["م2 ✅<br/>فكّ تشابك + استخراج"]
    M2 --> M3["م3 ✅<br/>فصل المحرّكَين + sad_runtime<br/>+ إغلاق التسرّب"]
    M3 --> M4["م4 ✅<br/>إعادة توصيل الأدوات"]
    M4 --> M5["م5 ✅<br/>إخلاء archived/"]
    M5 -.مؤجَّل.-> VM["إعادة كتابة الآلة<br/>⟶ مطابقة ثلاثيّة + توحيد الواجهات"]
    M5 -.أولويّة.-> CR["سدّ تباعد التعمية<br/>DIVERGENT(crypto)"]

    style M0 fill:#1b5e20,color:#fff
    style M1 fill:#1b5e20,color:#fff
    style M2 fill:#1b5e20,color:#fff
    style M3 fill:#1b5e20,color:#fff
    style M4 fill:#1b5e20,color:#fff
    style M5 fill:#1b5e20,color:#fff
    style VM fill:#37474f,color:#fff
    style CR fill:#b71c1c,color:#fff
```

</div>
