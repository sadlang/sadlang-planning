<div dir="rtl">

# 📊 مخططات خادم LSP للغة ص

مخططات تشغيليّة بصيغة **Mermaid** (نصّيّة، قابلة للمراجعة في PR). تغطّي: البنية، تدفّق البيانات من مصدر الحقيقة، نظام أوصاف الأداة، خريطة المزوّدات، وخارطة الطريق.

---

## 1) بنية المكوّنات

```mermaid
flowchart TB
    subgraph client["محرّر العميل (VS Code / Neovim …)"]
        ED["المحرّر"]
    end

    subgraph server["sad-lsp-server"]
        RPC["طبقة نقل JSON-RPC + main()"]
        subgraph engine["sad_lsp_engine — المحرّك"]
            CORE["النواة: مخزن المستندات + خطّ التحليل + فهرس الرموز"]
            PROV["المزوّدات (≈22): إكمال/تشخيص/تحويم/تنقّل/تلوين…"]
        end
    end

    subgraph shared["القلب المشترك"]
        SH["sad_shared: معجم + محلّل + AST"]
        TS["sad_type_system: تحليل الأنواع"]
        FMT["sad_formatter: تنسيق"]
    end

    ED <-->|"LSP عبر stdio"| RPC
    RPC --> CORE
    CORE --> PROV
    CORE --> SH
    PROV --> SH
    PROV --> TS
    PROV --> FMT
```

---

## 2) تدفّق البيانات — من مصدر الحقيقة إلى الميزة

```mermaid
flowchart LR
    subgraph sot["مصدر الحقيقة — language-truth/"]
        KW["keywords.yaml"]
        TY["types.yaml"]
        BI["builtins/*.yaml"]
        TM["type_methods.yaml"]
        ER["errors/*.yaml"]
    end

    subgraph gen["مولّدات وقت البناء — scripts/codegen/"]
        G["gen_*.py"]
    end

    subgraph hdr["ترويسات مولَّدة"]
        H["*_generated.h"]
    end

    subgraph eng["محرّك LSP"]
        L["sad_shared / sad_type_system"]
        P["المزوّدات"]
    end

    KW --> G
    TY --> G
    BI --> G
    TM --> G
    ER --> G
    G --> H
    H --> L
    L --> P
    P --> F["ميزة LSP: تحويم/إكمال/تلوين…"]
```

> المبدأ: تغيير سطرٍ في `language-truth/` يَسري آليًّا إلى الميزة عبر إعادة التوليد — **دون تعديل كود الأداة**.

---

## 3) نظام أوصاف التحويم المملوك للأداة (يستهلك المصدر ولا يوسّعه)

```mermaid
flowchart TB
    subgraph owned["نظام الأداة الداخليّ — tools/lsp/"]
        D["data/keyword_docs.yaml<br/>(أوصاف عرضٍ مملوكة للأداة)"]
        S["scripts/gen_keyword_docs.py"]
    end

    SOT["language-truth/keywords.yaml<br/>(مصدر الحقيقة — قراءة فقط)"]

    D --> S
    SOT -.->|"يستهلكه للتحقّق فقط"| S
    S -->|"يرفض أيّ مفتاح ليس كلمةً معجمية<br/>+ يوسّع الأسماء البديلة"| GENH["keyword_docs_generated.h<br/>(في مجلّد البناء — غير متتبَّع)"]
    GENH --> HOV["مزوّد التحويم"]

    style SOT fill:#eef,stroke:#88a
    style owned fill:#efe,stroke:#8a8
```

### أولويّة وصف التحويم

```mermaid
flowchart LR
    W["الكلمة تحت المؤشّر"] --> Q1{"نوع سطحيّ؟"}
    Q1 -->|نعم| T["وصف من types.yaml"]
    Q1 -->|لا| Q2{"وصف أداة موجود؟"}
    Q2 -->|نعم| TD["وصف نظام الأداة"]
    Q2 -->|لا| FB["وصف محرَّر احتياطًا"]
```

---

## 4) خريطة المزوّدات

```mermaid
mindmap
  root((خادم LSP))
    تحرير
      إكمال
      تلميح التواقيع
      التنسيق
      التنسيق أثناء الكتابة
    فهم
      تحويم
      تلوين دلاليّ
      تلميحات داخليّة
      عدسات الكود
    تنقّل
      تعريف
      مراجع
      رموز المستند
      روابط المستند
    بنية
      شجرة الاستدعاءات
      شجرة الأنواع
      نطاق التحديد
      طيّ
    جودة
      تشخيصات
      كاشف المشاكل المعروفة
      إعادة تسمية
      إجراءات الكود
```

---

## 5) خارطة الطريق (Gantt)

```mermaid
gantt
    title خارطة طريق خادم LSP للغة ص
    dateFormat YYYY-MM-DD
    axisFormat %m-%d

    section مكتمل
    توصيل القلب بمصدر الحقيقة      :done, m1, 2026-06-23, 2026-06-28

    section التوحيد والدقّة
    سجلّ مدمجات جامع (1073)         :m2, 2026-07-01, 20d
    دقّة التشخيصات                  :m3, after m2, 11d

    section الأداء والجودة
    التحليل التزايديّ والأداء       :m4, 2026-08-01, 20d
    اكتمال المزوّدات                :m5, 2026-08-10, 14d

    section الصيانة
    تنظيف ونشر وتوثيق               :m6, 2026-08-24, 8d
```

---

## 6) حالة المعالم

```mermaid
flowchart LR
    A["م1: توصيل المصدر ✅"] --> B["م2: سجلّ مدمجات جامع"]
    B --> C["م3: دقّة التشخيصات"]
    C --> D["م4: الأداء التزايديّ"]
    D --> E["م5: اكتمال المزوّدات"]
    E --> F["م6: تنظيف ونشر"]

    style A fill:#cfc,stroke:#393
    style B fill:#ffd,stroke:#aa3
    style C fill:#eee,stroke:#999
    style D fill:#eee,stroke:#999
    style E fill:#eee,stroke:#999
    style F fill:#eee,stroke:#999
```

</div>
