<div dir="rtl">

# 📐 مخططات مكتبة الرسومات (SadUI)

مخططات Mermaid تشغيليّة للمعماريّة ومسارات الكود وخطّ الربط وتدفّق إغلاق P0-3.

---

## 1) المعماريّة العامّة — مصدر واحد، محرّكان، بواطن متعدّدة

```mermaid
flowchart TD
    SRC["برنامج المستخدم (.ص)\nاستورد رسومات + واجهة + معدّلات"]
    SOT["مصدر الحقيقة\nlanguage-truth/builtins/ui_widgets.yaml"]
    PARSER["المحلّل المشترك\nshared/parser/"]
    AST["شجرة AST\nUIWidgetExprNode / UIModifierNode / UIStateDecl"]

    SRC --> PARSER
    SOT -. يغذّي الكتالوج .-> PARSER
    PARSER --> AST

    AST --> INTERP["محرّك المفسّر\nsad-run"]
    AST --> COMP["محرّك المترجم\nsad-build"]

    INTERP --> WB["WidgetBuilder\ninterpreter/src/ui/"]
    COMP --> SIR["SIR ثمّ LLVM IR\ncompiler/src/frontend + backend"]
    SIR --> RT["نداءات وقت التشغيل\nsad_button / sad_text / ..."]
    RT --> RTLIB["sad_rt_ui (جسر C)\nruntime/sad_ui_runtime.cpp"]

    WB --> CORE["نواة sad_ui\nIR + تخطيط RTL + Reconciler"]
    RTLIB --> CORE

    CORE --> BK_DESK["سطح المكتب\nSDL2 + OpenGL"]
    CORE --> BK_WEB["الويب\nHTML/CSS/JS"]
    CORE --> BK_IOS["iOS\nSwiftUI + Metal"]
    CORE --> BK_AND["أندرويد\nJNI (جزئيّ)"]

    classDef done fill:#1b5e20,stroke:#a5d6a7,color:#fff;
    classDef partial fill:#5d4037,stroke:#ffcc80,color:#fff;
    class INTERP,COMP,WB,CORE,RTLIB,BK_DESK,BK_WEB,BK_IOS done;
    class BK_AND partial;
```

---

## 2) مسارات الكود — من المصدر إلى الإطار المرسوم

```mermaid
flowchart LR
    subgraph SHARED["المشترك (shared/)"]
        P1["parser/src/ui/parser_ui.cpp"]
        P2["parser/src/declarations/parser_modules.cpp"]
        A1["ast/include/ui_nodes.h"]
        A2["ast/include/module_nodes.h"]
    end

    subgraph INT["المفسّر (interpreter/src/)"]
        I1["visitors/expression_evaluator_ui.cpp"]
        I2["ui/ui_widget_method_call.cpp"]
        I3["ui/widget_builder.cpp"]
        I4["ui/ui_bridge.cpp"]
    end

    subgraph COMP["المترجم (compiler/src/)"]
        C1["frontend/builders/builtins_ui.cpp"]
        C2["frontend/builders/call_method_dispatch.cpp"]
        C3["frontend/builders/statement_extension.cpp"]
        C4["backend/llvm/builders/platform/ui_ops.cpp"]
    end

    subgraph DRV["درايفر/ربط (tools/compiler/)"]
        D1["compiler_driver_build_utils.cpp"]
        D2["compiler_driver_lld.cpp"]
    end

    subgraph RTC["وقت التشغيل + النواة"]
        R1["runtime/sad_ui_runtime.cpp"]
        R2["sad_ui/ (النواة)"]
        R3["graphics/third_party/SDL2 + SDL2_ttf"]
    end

    SHARED --> INT
    SHARED --> COMP
    COMP --> DRV
    I3 --> R2
    C4 --> R1
    R1 --> R2
    DRV --> R3
    R2 --> R3
```

---

## 3) خطّ بناء وربط برنامج UI في المترجم

```mermaid
flowchart TD
    A["ui_min.ص"] --> B["المحلّل المشترك\n(parser_ui + parser_modules)"]
    B --> C["خفض أماميّ ⇒ SIR\nbuiltins_ui + call_method_dispatch"]
    C --> D["توليد LLVM IR\nui_ops ⇒ نداءات sad_*"]
    D --> E["ملفّ كائن (.obj)"]
    E --> F{"رابط lld-link\ncompiler_driver_lld.cpp"}
    F --> G["إلحاق مكتبات وقت التشغيل\ncompiler_driver_build_utils.cpp"]
    G --> H["sad_rt_ui → sad_ui"]
    G --> I["SDL2 + SDL2_ttf (مُورَّدة x64)"]
    H --> J["ملفّ تنفيذيّ"]
    I --> J
    J --> K["تشغيل ⇒ يطابق المفسّر 5/5"]

    classDef ok fill:#1b5e20,stroke:#a5d6a7,color:#fff;
    class A,B,C,D,E,F,G,H,I,J,K ok;
```

---

## 4) تدفّق إغلاق P0-3 — الطبقات الأربع

```mermaid
flowchart TD
    START["sad-build على ui_min.ص"] --> L1{"أ-2a: صدّر * المجرّد\nمقبول في المحلّل؟"}
    L1 -- "لا ⇒ يفشل تحليل رسومات.ص" --> F1["إصلاح: دلالة صدّر-كل-الوحدة\nمسار فارغ + wildcard"]
    F1 --> L2
    L1 -- "نعم" --> L2{"أ-2b: نص_عنصر مربوط؟"}
    L2 -- "لا ⇒ VOID صامت" --> F2["إصلاح: مطابقة\nنص_عنصر + نص_عرض"]
    F2 --> L3
    L2 -- "نعم" --> L3{"أ-3: معدّل انسيابيّ\nيُعيد قيمة؟"}
    L3 -- "لا ⇒ VOID ⇒ getNullValue(void) انهيار" --> F3["إصلاح: نداء المعدّل\nيُعيد مقبض العنصر"]
    F3 --> L4
    L3 -- "نعم" --> L4{"أ-4: مكتبة وقت\nتشغيل الواجهات مربوطة؟"}
    L4 -- "لا ⇒ undefined sad_button" --> F4["إصلاح: إلحاق\nsad_rt_ui→sad_ui + SDL2"]
    F4 --> DONE
    L4 -- "نعم" --> DONE["تنفيذيّ يعمل = المفسّر 5/5"]

    classDef fix fill:#0d47a1,stroke:#90caf9,color:#fff;
    classDef ok fill:#1b5e20,stroke:#a5d6a7,color:#fff;
    class F1,F2,F3,F4 fix;
    class DONE ok;
```

---

## 5) خفض المعدّلات: المفسّر مقابل المترجم

```mermaid
flowchart TD
    EXPR["زر('زيادة').لون('أخضر').عند_النقر(دالة)"]

    EXPR --> INT["المفسّر"]
    EXPR --> COMP["المترجم"]

    subgraph IB["interpreter/src/ui/ui_widget_method_call.cpp"]
        INT --> IW{"المستقبِل WidgetBuilder؟"}
        IW -- "نعم" --> IAPPLY["يطبّق الأثر (خاصّيّة/حدث)\nثمّ يُعيد العنصر نفسه"]
    end

    subgraph CB["compiler/src/frontend/builders/call_method_dispatch.cpp"]
        COMP --> CW{"مقبض Pointer\nبلا صنفٍ مُستنتَج؟"}
        CW -- "نعم" --> CRET["خفض انسيابيّ:\nيُعيد مقبض العنصر (Pointer)"]
        CRET -. "شريحة تالية: ABI عامّ\nلتطبيق الأثر المرسوم" .-> CTODO["م-أ3ر"]
    end

    IAPPLY --> EQ["النتيجة: قيمة «كائن» تتسلسل"]
    CRET --> EQ
```

---

## 6) حالة المعالم

```mermaid
flowchart LR
    P01["P0-1 وسم الكائن\n#62"]:::done --> P02["P0-2 واجهة + @حالة\n#67"]:::done
    P02 --> P03["P0-3 ترجمة طرفًا لطرف (headless)\n#119"]:::done
    P03 --> M3R["م-أ3ر أثر المعدّلات المرسوم"]:::todo
    P03 --> M4P["م-أ4ع ربط POSIX + SDL2_ttf"]:::todo
    P03 --> MCOV["م-تغطية توسيع المطابقة"]:::todo

    classDef done fill:#1b5e20,stroke:#a5d6a7,color:#fff;
    classDef todo fill:#5d4037,stroke:#ffcc80,color:#fff;
```

---

## 7) تسلسل التشغيل طرفًا لطرف

```mermaid
sequenceDiagram
    autonumber
    participant U as المستخدم
    participant SB as sad-build
    participant LLD as lld-link
    participant RT as sad_rt_ui / sad_ui
    participant EXE as التنفيذيّ
    participant SR as sad-run (مرجع)

    U->>SB: ترجمة ui_min.ص
    SB->>SB: تحليل + خفض SIR + توليد IR
    SB->>LLD: ربط (.obj)
    LLD->>RT: حلّ sad_button/sad_text/sad_column
    LLD->>EXE: إنتاج التنفيذيّ
    U->>EXE: تشغيل
    EXE-->>U: نجح 5 / فشل 0 ✅
    U->>SR: تشغيل المرجع على ui_min.ص
    SR-->>U: نجح 5 / فشل 0 ✅
    Note over EXE,SR: تطابق المخرَج ⇒ بوّابة المطابقة مجتازة
```

---

> ⚠️ محتوى **عامّ** — لا أرقام ماليّة ولا أسرار. راجع [GOVERNANCE.md](../../../GOVERNANCE.md).

</div>
