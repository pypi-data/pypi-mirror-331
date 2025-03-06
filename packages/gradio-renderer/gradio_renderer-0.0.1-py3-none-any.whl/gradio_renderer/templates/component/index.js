const {
  SvelteComponent: Je,
  append_hydration: Ke,
  attr: F,
  children: Qe,
  claim_element: ue,
  detach: ee,
  element: _e,
  empty: fe,
  init: Re,
  insert_hydration: Ce,
  noop: ce,
  safe_not_equal: Xe,
  src_url_equal: me,
  toggle_class: P
} = window.__gradio__svelte__internal;
function de(a) {
  let l, t, e;
  return {
    c() {
      l = _e("div"), t = _e("img"), this.h();
    },
    l(n) {
      l = ue(n, "DIV", { class: !0 });
      var i = Qe(l);
      t = ue(i, "IMG", { src: !0, alt: !0, class: !0 }), i.forEach(ee), this.h();
    },
    h() {
      me(t.src, e = /*value*/
      a[0].url) || F(t, "src", e), F(t, "alt", ""), F(t, "class", "svelte-giydt1"), F(l, "class", "container svelte-giydt1"), P(
        l,
        "table",
        /*type*/
        a[1] === "table"
      ), P(
        l,
        "gallery",
        /*type*/
        a[1] === "gallery"
      ), P(
        l,
        "selected",
        /*selected*/
        a[2]
      );
    },
    m(n, i) {
      Ce(n, l, i), Ke(l, t);
    },
    p(n, i) {
      i & /*value*/
      1 && !me(t.src, e = /*value*/
      n[0].url) && F(t, "src", e), i & /*type*/
      2 && P(
        l,
        "table",
        /*type*/
        n[1] === "table"
      ), i & /*type*/
      2 && P(
        l,
        "gallery",
        /*type*/
        n[1] === "gallery"
      ), i & /*selected*/
      4 && P(
        l,
        "selected",
        /*selected*/
        n[2]
      );
    },
    d(n) {
      n && ee(l);
    }
  };
}
function Ye(a) {
  let l, t = (
    /*value*/
    a[0] && de(a)
  );
  return {
    c() {
      t && t.c(), l = fe();
    },
    l(e) {
      t && t.l(e), l = fe();
    },
    m(e, n) {
      t && t.m(e, n), Ce(e, l, n);
    },
    p(e, [n]) {
      /*value*/
      e[0] ? t ? t.p(e, n) : (t = de(e), t.c(), t.m(l.parentNode, l)) : t && (t.d(1), t = null);
    },
    i: ce,
    o: ce,
    d(e) {
      e && ee(l), t && t.d(e);
    }
  };
}
function Ze(a, l, t) {
  let { value: e } = l, { type: n } = l, { selected: i = !1 } = l;
  return a.$$set = (r) => {
    "value" in r && t(0, e = r.value), "type" in r && t(1, n = r.type), "selected" in r && t(2, i = r.selected);
  }, [e, n, i];
}
class Ml extends Je {
  constructor(l) {
    super(), Re(this, l, Ze, Ye, Xe, { value: 0, type: 1, selected: 2 });
  }
}
const {
  SvelteComponent: ye,
  append_hydration: ge,
  attr: z,
  check_outros: De,
  children: he,
  claim_component: j,
  claim_element: Y,
  claim_space: Ue,
  create_component: O,
  destroy_component: W,
  detach: N,
  element: Z,
  empty: K,
  group_outros: Ne,
  init: xe,
  insert_hydration: H,
  mount_component: A,
  safe_not_equal: el,
  space: Te,
  src_url_equal: be,
  toggle_class: we,
  transition_in: I,
  transition_out: B
} = window.__gradio__svelte__internal;
function ll(a) {
  let l, t, e, n, i, r, u;
  return l = new IconButtonWrapper({
    props: {
      $$slots: { default: [al] },
      $$scope: { ctx: a }
    }
  }), {
    c() {
      O(l.$$.fragment), t = Te(), e = Z("button"), n = Z("div"), i = Z("img"), this.h();
    },
    l(s) {
      j(l.$$.fragment, s), t = Ue(s), e = Y(s, "BUTTON", { class: !0 });
      var f = he(e);
      n = Y(f, "DIV", { class: !0 });
      var o = he(n);
      i = Y(o, "IMG", { src: !0, alt: !0, loading: !0 }), o.forEach(N), f.forEach(N), this.h();
    },
    h() {
      be(i.src, r = /*value*/
      a[0].url) || z(i, "src", r), z(i, "alt", ""), z(i, "loading", "lazy"), z(n, "class", "image-container svelte-mdifpc"), we(
        n,
        "selectable",
        /*selectable*/
        a[4]
      ), z(e, "class", "svelte-mdifpc");
    },
    m(s, f) {
      A(l, s, f), H(s, t, f), H(s, e, f), ge(e, n), ge(n, i), u = !0;
    },
    p(s, f) {
      const o = {};
      f & /*$$scope, value, i18n, show_download_button*/
      105 && (o.$$scope = { dirty: f, ctx: s }), l.$set(o), (!u || f & /*value*/
      1 && !be(i.src, r = /*value*/
      s[0].url)) && z(i, "src", r), (!u || f & /*selectable*/
      16) && we(
        n,
        "selectable",
        /*selectable*/
        s[4]
      );
    },
    i(s) {
      u || (I(l.$$.fragment, s), u = !0);
    },
    o(s) {
      B(l.$$.fragment, s), u = !1;
    },
    d(s) {
      s && (N(t), N(e)), W(l, s);
    }
  };
}
function tl(a) {
  let l, t;
  return l = new Empty({
    props: {
      unpadded_box: !0,
      size: "large",
      $$slots: { default: [il] },
      $$scope: { ctx: a }
    }
  }), {
    c() {
      O(l.$$.fragment);
    },
    l(e) {
      j(l.$$.fragment, e);
    },
    m(e, n) {
      A(l, e, n), t = !0;
    },
    p(e, n) {
      const i = {};
      n & /*$$scope*/
      64 && (i.$$scope = { dirty: n, ctx: e }), l.$set(i);
    },
    i(e) {
      t || (I(l.$$.fragment, e), t = !0);
    },
    o(e) {
      B(l.$$.fragment, e), t = !1;
    },
    d(e) {
      W(l, e);
    }
  };
}
function $e(a) {
  let l, t;
  return l = new DownloadLink({
    props: {
      href: (
        /*value*/
        a[0].url
      ),
      download: (
        /*value*/
        a[0].orig_name || "image"
      ),
      $$slots: { default: [nl] },
      $$scope: { ctx: a }
    }
  }), {
    c() {
      O(l.$$.fragment);
    },
    l(e) {
      j(l.$$.fragment, e);
    },
    m(e, n) {
      A(l, e, n), t = !0;
    },
    p(e, n) {
      const i = {};
      n & /*value*/
      1 && (i.href = /*value*/
      e[0].url), n & /*value*/
      1 && (i.download = /*value*/
      e[0].orig_name || "image"), n & /*$$scope, i18n*/
      96 && (i.$$scope = { dirty: n, ctx: e }), l.$set(i);
    },
    i(e) {
      t || (I(l.$$.fragment, e), t = !0);
    },
    o(e) {
      B(l.$$.fragment, e), t = !1;
    },
    d(e) {
      W(l, e);
    }
  };
}
function nl(a) {
  let l, t;
  return l = new IconButton({
    props: {
      Icon: Download,
      label: (
        /*i18n*/
        a[5]("common.download")
      )
    }
  }), {
    c() {
      O(l.$$.fragment);
    },
    l(e) {
      j(l.$$.fragment, e);
    },
    m(e, n) {
      A(l, e, n), t = !0;
    },
    p(e, n) {
      const i = {};
      n & /*i18n*/
      32 && (i.label = /*i18n*/
      e[5]("common.download")), l.$set(i);
    },
    i(e) {
      t || (I(l.$$.fragment, e), t = !0);
    },
    o(e) {
      B(l.$$.fragment, e), t = !1;
    },
    d(e) {
      W(l, e);
    }
  };
}
function al(a) {
  let l, t, e = (
    /*show_download_button*/
    a[3] && $e(a)
  );
  return {
    c() {
      e && e.c(), l = K();
    },
    l(n) {
      e && e.l(n), l = K();
    },
    m(n, i) {
      e && e.m(n, i), H(n, l, i), t = !0;
    },
    p(n, i) {
      /*show_download_button*/
      n[3] ? e ? (e.p(n, i), i & /*show_download_button*/
      8 && I(e, 1)) : (e = $e(n), e.c(), I(e, 1), e.m(l.parentNode, l)) : e && (Ne(), B(e, 1, 1, () => {
        e = null;
      }), De());
    },
    i(n) {
      t || (I(e), t = !0);
    },
    o(n) {
      B(e), t = !1;
    },
    d(n) {
      n && N(l), e && e.d(n);
    }
  };
}
function il(a) {
  let l, t;
  return l = new ImageIcon({}), {
    c() {
      O(l.$$.fragment);
    },
    l(e) {
      j(l.$$.fragment, e);
    },
    m(e, n) {
      A(l, e, n), t = !0;
    },
    i(e) {
      t || (I(l.$$.fragment, e), t = !0);
    },
    o(e) {
      B(l.$$.fragment, e), t = !1;
    },
    d(e) {
      W(l, e);
    }
  };
}
function ol(a) {
  let l, t, e, n, i, r;
  l = new BlockLabel({
    props: {
      show_label: (
        /*show_label*/
        a[2]
      ),
      Icon: ImageIcon,
      label: (
        /*label*/
        a[1] || /*i18n*/
        a[5]("image.image")
      )
    }
  });
  const u = [tl, ll], s = [];
  function f(o, _) {
    return (
      /*value*/
      o[0] === null || !/*value*/
      o[0].url ? 0 : 1
    );
  }
  return e = f(a), n = s[e] = u[e](a), {
    c() {
      O(l.$$.fragment), t = Te(), n.c(), i = K();
    },
    l(o) {
      j(l.$$.fragment, o), t = Ue(o), n.l(o), i = K();
    },
    m(o, _) {
      A(l, o, _), H(o, t, _), s[e].m(o, _), H(o, i, _), r = !0;
    },
    p(o, [_]) {
      const w = {};
      _ & /*show_label*/
      4 && (w.show_label = /*show_label*/
      o[2]), _ & /*label, i18n*/
      34 && (w.label = /*label*/
      o[1] || /*i18n*/
      o[5]("image.image")), l.$set(w);
      let b = e;
      e = f(o), e === b ? s[e].p(o, _) : (Ne(), B(s[b], 1, 1, () => {
        s[b] = null;
      }), De(), n = s[e], n ? n.p(o, _) : (n = s[e] = u[e](o), n.c()), I(n, 1), n.m(i.parentNode, i));
    },
    i(o) {
      r || (I(l.$$.fragment, o), I(n), r = !0);
    },
    o(o) {
      B(l.$$.fragment, o), B(n), r = !1;
    },
    d(o) {
      o && (N(t), N(i)), W(l, o), s[e].d(o);
    }
  };
}
function sl(a, l, t) {
  let { value: e } = l, { label: n = void 0 } = l, { show_label: i } = l, { show_download_button: r = !0 } = l, { selectable: u = !1 } = l, { i18n: s } = l;
  return a.$$set = (f) => {
    "value" in f && t(0, e = f.value), "label" in f && t(1, n = f.label), "show_label" in f && t(2, i = f.show_label), "show_download_button" in f && t(3, r = f.show_download_button), "selectable" in f && t(4, u = f.selectable), "i18n" in f && t(5, s = f.i18n);
  }, [e, n, i, r, u, s];
}
let Pl = class extends ye {
  constructor(l) {
    super(), xe(this, l, sl, ol, el, {
      value: 0,
      label: 1,
      show_label: 2,
      show_download_button: 3,
      selectable: 4,
      i18n: 5
    });
  }
};
const {
  SvelteComponent: rl,
  add_flush_callback: pe,
  append_hydration: J,
  attr: C,
  bind: ve,
  binding_callbacks: le,
  bubble: ul,
  check_outros: Ve,
  children: te,
  claim_component: ne,
  claim_element: Q,
  claim_space: y,
  create_component: ae,
  create_slot: _l,
  destroy_component: ie,
  detach: T,
  element: R,
  empty: ke,
  get_all_dirty_from_scope: fl,
  get_slot_changes: cl,
  group_outros: Ge,
  init: ml,
  insert_hydration: X,
  mount_component: oe,
  noop: dl,
  safe_not_equal: gl,
  space: x,
  src_url_equal: Ie,
  transition_in: q,
  transition_out: D,
  update_slot_base: hl
} = window.__gradio__svelte__internal, { createEventDispatcher: bl } = window.__gradio__svelte__internal;
function qe(a) {
  let l, t;
  return l = new ClearImage({}), l.$on(
    "remove_image",
    /*remove_image_handler*/
    a[12]
  ), {
    c() {
      ae(l.$$.fragment);
    },
    l(e) {
      ne(l.$$.fragment, e);
    },
    m(e, n) {
      oe(l, e, n), t = !0;
    },
    p: dl,
    i(e) {
      t || (q(l.$$.fragment, e), t = !0);
    },
    o(e) {
      D(l.$$.fragment, e), t = !1;
    },
    d(e) {
      ie(l, e);
    }
  };
}
function Be(a) {
  let l;
  const t = (
    /*#slots*/
    a[11].default
  ), e = _l(
    t,
    a,
    /*$$scope*/
    a[17],
    null
  );
  return {
    c() {
      e && e.c();
    },
    l(n) {
      e && e.l(n);
    },
    m(n, i) {
      e && e.m(n, i), l = !0;
    },
    p(n, i) {
      e && e.p && (!l || i & /*$$scope*/
      131072) && hl(
        e,
        t,
        n,
        /*$$scope*/
        n[17],
        l ? cl(
          t,
          /*$$scope*/
          n[17],
          i,
          null
        ) : fl(
          /*$$scope*/
          n[17]
        ),
        null
      );
    },
    i(n) {
      l || (q(e, n), l = !0);
    },
    o(n) {
      D(e, n), l = !1;
    },
    d(n) {
      e && e.d(n);
    }
  };
}
function wl(a) {
  let l, t, e = (
    /*value*/
    a[0] === null && Be(a)
  );
  return {
    c() {
      e && e.c(), l = ke();
    },
    l(n) {
      e && e.l(n), l = ke();
    },
    m(n, i) {
      e && e.m(n, i), X(n, l, i), t = !0;
    },
    p(n, i) {
      /*value*/
      n[0] === null ? e ? (e.p(n, i), i & /*value*/
      1 && q(e, 1)) : (e = Be(n), e.c(), q(e, 1), e.m(l.parentNode, l)) : e && (Ge(), D(e, 1, 1, () => {
        e = null;
      }), Ve());
    },
    i(n) {
      t || (q(e), t = !0);
    },
    o(n) {
      D(e), t = !1;
    },
    d(n) {
      n && T(l), e && e.d(n);
    }
  };
}
function Ee(a) {
  let l, t, e, n;
  return {
    c() {
      l = R("div"), t = R("img"), this.h();
    },
    l(i) {
      l = Q(i, "DIV", { class: !0 });
      var r = te(l);
      t = Q(r, "IMG", { src: !0, alt: !0 }), r.forEach(T), this.h();
    },
    h() {
      Ie(t.src, e = /*value*/
      a[0].url) || C(t, "src", e), C(t, "alt", n = /*value*/
      a[0].alt_text), C(l, "class", "image-frame svelte-1mw9bca");
    },
    m(i, r) {
      X(i, l, r), J(l, t);
    },
    p(i, r) {
      r & /*value*/
      1 && !Ie(t.src, e = /*value*/
      i[0].url) && C(t, "src", e), r & /*value*/
      1 && n !== (n = /*value*/
      i[0].alt_text) && C(t, "alt", n);
    },
    d(i) {
      i && T(l);
    }
  };
}
function $l(a) {
  var U;
  let l, t, e, n, i, r, u, s, f, o;
  l = new BlockLabel({
    props: {
      show_label: (
        /*show_label*/
        a[2]
      ),
      Icon: ImageIcon,
      label: (
        /*label*/
        a[1] || "Image"
      )
    }
  });
  let _ = (
    /*value*/
    ((U = a[0]) == null ? void 0 : U.url) && qe(a)
  );
  function w(c) {
    a[14](c);
  }
  function b(c) {
    a[15](c);
  }
  let k = {
    upload: (
      /*upload*/
      a[4]
    ),
    stream_handler: (
      /*stream_handler*/
      a[5]
    ),
    hidden: (
      /*value*/
      a[0] !== null
    ),
    filetype: "image/*",
    root: (
      /*root*/
      a[3]
    ),
    $$slots: { default: [wl] },
    $$scope: { ctx: a }
  };
  /*uploading*/
  a[6] !== void 0 && (k.uploading = /*uploading*/
  a[6]), /*dragging*/
  a[7] !== void 0 && (k.dragging = /*dragging*/
  a[7]), r = new Upload({ props: k }), a[13](r), le.push(() => ve(r, "uploading", w)), le.push(() => ve(r, "dragging", b)), r.$on(
    "load",
    /*handle_upload*/
    a[9]
  ), r.$on(
    "error",
    /*error_handler*/
    a[16]
  );
  let h = (
    /*value*/
    a[0] !== null && Ee(a)
  );
  return {
    c() {
      ae(l.$$.fragment), t = x(), e = R("div"), _ && _.c(), n = x(), i = R("div"), ae(r.$$.fragment), f = x(), h && h.c(), this.h();
    },
    l(c) {
      ne(l.$$.fragment, c), t = y(c), e = Q(c, "DIV", { "data-testid": !0, class: !0 });
      var g = te(e);
      _ && _.l(g), n = y(g), i = Q(g, "DIV", { class: !0 });
      var p = te(i);
      ne(r.$$.fragment, p), f = y(p), h && h.l(p), p.forEach(T), g.forEach(T), this.h();
    },
    h() {
      C(i, "class", "upload-container svelte-1mw9bca"), C(e, "data-testid", "image"), C(e, "class", "image-container svelte-1mw9bca");
    },
    m(c, g) {
      oe(l, c, g), X(c, t, g), X(c, e, g), _ && _.m(e, null), J(e, n), J(e, i), oe(r, i, null), J(i, f), h && h.m(i, null), o = !0;
    },
    p(c, [g]) {
      var d;
      const p = {};
      g & /*show_label*/
      4 && (p.show_label = /*show_label*/
      c[2]), g & /*label*/
      2 && (p.label = /*label*/
      c[1] || "Image"), l.$set(p), /*value*/
      (d = c[0]) != null && d.url ? _ ? (_.p(c, g), g & /*value*/
      1 && q(_, 1)) : (_ = qe(c), _.c(), q(_, 1), _.m(e, n)) : _ && (Ge(), D(_, 1, 1, () => {
        _ = null;
      }), Ve());
      const v = {};
      g & /*upload*/
      16 && (v.upload = /*upload*/
      c[4]), g & /*stream_handler*/
      32 && (v.stream_handler = /*stream_handler*/
      c[5]), g & /*value*/
      1 && (v.hidden = /*value*/
      c[0] !== null), g & /*root*/
      8 && (v.root = /*root*/
      c[3]), g & /*$$scope, value*/
      131073 && (v.$$scope = { dirty: g, ctx: c }), !u && g & /*uploading*/
      64 && (u = !0, v.uploading = /*uploading*/
      c[6], pe(() => u = !1)), !s && g & /*dragging*/
      128 && (s = !0, v.dragging = /*dragging*/
      c[7], pe(() => s = !1)), r.$set(v), /*value*/
      c[0] !== null ? h ? h.p(c, g) : (h = Ee(c), h.c(), h.m(i, null)) : h && (h.d(1), h = null);
    },
    i(c) {
      o || (q(l.$$.fragment, c), q(_), q(r.$$.fragment, c), o = !0);
    },
    o(c) {
      D(l.$$.fragment, c), D(_), D(r.$$.fragment, c), o = !1;
    },
    d(c) {
      c && (T(t), T(e)), ie(l, c), _ && _.d(), a[13](null), ie(r), h && h.d();
    }
  };
}
function pl(a, l, t) {
  let { $$slots: e = {}, $$scope: n } = l, { value: i } = l, { label: r = void 0 } = l, { show_label: u } = l, { root: s } = l, { upload: f } = l, { stream_handler: o } = l, _, w = !1;
  function b({ detail: d }) {
    t(0, i = d), k("upload");
  }
  const k = bl();
  let h = !1;
  const U = () => {
    t(0, i = null), k("clear");
  };
  function c(d) {
    le[d ? "unshift" : "push"](() => {
      _ = d, t(8, _);
    });
  }
  function g(d) {
    w = d, t(6, w);
  }
  function p(d) {
    h = d, t(7, h);
  }
  function v(d) {
    ul.call(this, a, d);
  }
  return a.$$set = (d) => {
    "value" in d && t(0, i = d.value), "label" in d && t(1, r = d.label), "show_label" in d && t(2, u = d.show_label), "root" in d && t(3, s = d.root), "upload" in d && t(4, f = d.upload), "stream_handler" in d && t(5, o = d.stream_handler), "$$scope" in d && t(17, n = d.$$scope);
  }, a.$$.update = () => {
    a.$$.dirty & /*uploading*/
    64 && w && t(0, i = null), a.$$.dirty & /*dragging*/
    128 && k("drag", h);
  }, [
    i,
    r,
    u,
    s,
    f,
    o,
    w,
    h,
    _,
    b,
    k,
    e,
    U,
    c,
    g,
    p,
    v,
    n
  ];
}
let jl = class extends rl {
  constructor(l) {
    super(), ml(this, l, pl, $l, gl, {
      value: 0,
      label: 1,
      show_label: 2,
      root: 3,
      upload: 4,
      stream_handler: 5
    });
  }
};
const {
  SvelteComponent: vl,
  add_flush_callback: kl,
  assign: Le,
  bind: Il,
  binding_callbacks: ql,
  check_outros: Bl,
  claim_component: V,
  claim_space: Me,
  create_component: G,
  destroy_component: L,
  detach: se,
  empty: Se,
  flush: $,
  get_spread_object: Pe,
  get_spread_update: ze,
  group_outros: El,
  init: Sl,
  insert_hydration: re,
  mount_component: M,
  safe_not_equal: Cl,
  space: je,
  transition_in: E,
  transition_out: S
} = window.__gradio__svelte__internal;
function Dl(a) {
  let l, t;
  return l = new Block({
    props: {
      visible: (
        /*visible*/
        a[3]
      ),
      variant: (
        /*value*/
        a[0] === null ? "dashed" : "solid"
      ),
      border_mode: (
        /*dragging*/
        a[15] ? "focus" : "base"
      ),
      padding: !1,
      elem_id: (
        /*elem_id*/
        a[1]
      ),
      elem_classes: (
        /*elem_classes*/
        a[2]
      ),
      allow_overflow: !1,
      container: (
        /*container*/
        a[7]
      ),
      scale: (
        /*scale*/
        a[8]
      ),
      min_width: (
        /*min_width*/
        a[9]
      ),
      $$slots: { default: [Tl] },
      $$scope: { ctx: a }
    }
  }), {
    c() {
      G(l.$$.fragment);
    },
    l(e) {
      V(l.$$.fragment, e);
    },
    m(e, n) {
      M(l, e, n), t = !0;
    },
    p(e, n) {
      const i = {};
      n & /*visible*/
      8 && (i.visible = /*visible*/
      e[3]), n & /*value*/
      1 && (i.variant = /*value*/
      e[0] === null ? "dashed" : "solid"), n & /*dragging*/
      32768 && (i.border_mode = /*dragging*/
      e[15] ? "focus" : "base"), n & /*elem_id*/
      2 && (i.elem_id = /*elem_id*/
      e[1]), n & /*elem_classes*/
      4 && (i.elem_classes = /*elem_classes*/
      e[2]), n & /*container*/
      128 && (i.container = /*container*/
      e[7]), n & /*scale*/
      256 && (i.scale = /*scale*/
      e[8]), n & /*min_width*/
      512 && (i.min_width = /*min_width*/
      e[9]), n & /*$$scope, gradio, root, label, show_label, value, dragging, placeholder, loading_status*/
      16839729 && (i.$$scope = { dirty: n, ctx: e }), l.$set(i);
    },
    i(e) {
      t || (E(l.$$.fragment, e), t = !0);
    },
    o(e) {
      S(l.$$.fragment, e), t = !1;
    },
    d(e) {
      L(l, e);
    }
  };
}
function Ul(a) {
  let l, t;
  return l = new Block({
    props: {
      visible: (
        /*visible*/
        a[3]
      ),
      variant: "solid",
      border_mode: (
        /*dragging*/
        a[15] ? "focus" : "base"
      ),
      padding: !1,
      elem_id: (
        /*elem_id*/
        a[1]
      ),
      elem_classes: (
        /*elem_classes*/
        a[2]
      ),
      allow_overflow: !1,
      container: (
        /*container*/
        a[7]
      ),
      scale: (
        /*scale*/
        a[8]
      ),
      min_width: (
        /*min_width*/
        a[9]
      ),
      $$slots: { default: [Vl] },
      $$scope: { ctx: a }
    }
  }), {
    c() {
      G(l.$$.fragment);
    },
    l(e) {
      V(l.$$.fragment, e);
    },
    m(e, n) {
      M(l, e, n), t = !0;
    },
    p(e, n) {
      const i = {};
      n & /*visible*/
      8 && (i.visible = /*visible*/
      e[3]), n & /*dragging*/
      32768 && (i.border_mode = /*dragging*/
      e[15] ? "focus" : "base"), n & /*elem_id*/
      2 && (i.elem_id = /*elem_id*/
      e[1]), n & /*elem_classes*/
      4 && (i.elem_classes = /*elem_classes*/
      e[2]), n & /*container*/
      128 && (i.container = /*container*/
      e[7]), n & /*scale*/
      256 && (i.scale = /*scale*/
      e[8]), n & /*min_width*/
      512 && (i.min_width = /*min_width*/
      e[9]), n & /*$$scope, value, label, show_label, show_download_button, gradio, loading_status*/
      16794737 && (i.$$scope = { dirty: n, ctx: e }), l.$set(i);
    },
    i(e) {
      t || (E(l.$$.fragment, e), t = !0);
    },
    o(e) {
      S(l.$$.fragment, e), t = !1;
    },
    d(e) {
      L(l, e);
    }
  };
}
function Nl(a) {
  let l, t;
  return l = new UploadText({
    props: {
      i18n: (
        /*gradio*/
        a[14].i18n
      ),
      type: "image",
      placeholder: (
        /*placeholder*/
        a[13]
      )
    }
  }), {
    c() {
      G(l.$$.fragment);
    },
    l(e) {
      V(l.$$.fragment, e);
    },
    m(e, n) {
      M(l, e, n), t = !0;
    },
    p(e, n) {
      const i = {};
      n & /*gradio*/
      16384 && (i.i18n = /*gradio*/
      e[14].i18n), n & /*placeholder*/
      8192 && (i.placeholder = /*placeholder*/
      e[13]), l.$set(i);
    },
    i(e) {
      t || (E(l.$$.fragment, e), t = !0);
    },
    o(e) {
      S(l.$$.fragment, e), t = !1;
    },
    d(e) {
      L(l, e);
    }
  };
}
function Tl(a) {
  let l, t, e, n, i;
  const r = [
    {
      autoscroll: (
        /*gradio*/
        a[14].autoscroll
      )
    },
    { i18n: (
      /*gradio*/
      a[14].i18n
    ) },
    /*loading_status*/
    a[10]
  ];
  let u = {};
  for (let o = 0; o < r.length; o += 1)
    u = Le(u, r[o]);
  l = new StatusTracker({ props: u }), l.$on(
    "clear_status",
    /*clear_status_handler_1*/
    a[17]
  );
  function s(o) {
    a[20](o);
  }
  let f = {
    upload: (
      /*func*/
      a[18]
    ),
    stream_handler: (
      /*func_1*/
      a[19]
    ),
    root: (
      /*root*/
      a[12]
    ),
    label: (
      /*label*/
      a[4]
    ),
    show_label: (
      /*show_label*/
      a[5]
    ),
    $$slots: { default: [Nl] },
    $$scope: { ctx: a }
  };
  return (
    /*value*/
    a[0] !== void 0 && (f.value = /*value*/
    a[0]), e = new ImageUploader({ props: f }), ql.push(() => Il(e, "value", s)), e.$on(
      "clear",
      /*clear_handler*/
      a[21]
    ), e.$on(
      "drag",
      /*drag_handler*/
      a[22]
    ), e.$on(
      "upload",
      /*upload_handler*/
      a[23]
    ), {
      c() {
        G(l.$$.fragment), t = je(), G(e.$$.fragment);
      },
      l(o) {
        V(l.$$.fragment, o), t = Me(o), V(e.$$.fragment, o);
      },
      m(o, _) {
        M(l, o, _), re(o, t, _), M(e, o, _), i = !0;
      },
      p(o, _) {
        const w = _ & /*gradio, loading_status*/
        17408 ? ze(r, [
          _ & /*gradio*/
          16384 && {
            autoscroll: (
              /*gradio*/
              o[14].autoscroll
            )
          },
          _ & /*gradio*/
          16384 && { i18n: (
            /*gradio*/
            o[14].i18n
          ) },
          _ & /*loading_status*/
          1024 && Pe(
            /*loading_status*/
            o[10]
          )
        ]) : {};
        l.$set(w);
        const b = {};
        _ & /*gradio*/
        16384 && (b.upload = /*func*/
        o[18]), _ & /*gradio*/
        16384 && (b.stream_handler = /*func_1*/
        o[19]), _ & /*root*/
        4096 && (b.root = /*root*/
        o[12]), _ & /*label*/
        16 && (b.label = /*label*/
        o[4]), _ & /*show_label*/
        32 && (b.show_label = /*show_label*/
        o[5]), _ & /*$$scope, gradio, placeholder*/
        16801792 && (b.$$scope = { dirty: _, ctx: o }), !n && _ & /*value*/
        1 && (n = !0, b.value = /*value*/
        o[0], kl(() => n = !1)), e.$set(b);
      },
      i(o) {
        i || (E(l.$$.fragment, o), E(e.$$.fragment, o), i = !0);
      },
      o(o) {
        S(l.$$.fragment, o), S(e.$$.fragment, o), i = !1;
      },
      d(o) {
        o && se(t), L(l, o), L(e, o);
      }
    }
  );
}
function Vl(a) {
  let l, t, e, n;
  const i = [
    {
      autoscroll: (
        /*gradio*/
        a[14].autoscroll
      )
    },
    { i18n: (
      /*gradio*/
      a[14].i18n
    ) },
    /*loading_status*/
    a[10]
  ];
  let r = {};
  for (let u = 0; u < i.length; u += 1)
    r = Le(r, i[u]);
  return l = new StatusTracker({ props: r }), l.$on(
    "clear_status",
    /*clear_status_handler*/
    a[16]
  ), e = new ImagePreview({
    props: {
      value: (
        /*value*/
        a[0]
      ),
      label: (
        /*label*/
        a[4]
      ),
      show_label: (
        /*show_label*/
        a[5]
      ),
      show_download_button: (
        /*show_download_button*/
        a[6]
      ),
      i18n: (
        /*gradio*/
        a[14].i18n
      )
    }
  }), {
    c() {
      G(l.$$.fragment), t = je(), G(e.$$.fragment);
    },
    l(u) {
      V(l.$$.fragment, u), t = Me(u), V(e.$$.fragment, u);
    },
    m(u, s) {
      M(l, u, s), re(u, t, s), M(e, u, s), n = !0;
    },
    p(u, s) {
      const f = s & /*gradio, loading_status*/
      17408 ? ze(i, [
        s & /*gradio*/
        16384 && {
          autoscroll: (
            /*gradio*/
            u[14].autoscroll
          )
        },
        s & /*gradio*/
        16384 && { i18n: (
          /*gradio*/
          u[14].i18n
        ) },
        s & /*loading_status*/
        1024 && Pe(
          /*loading_status*/
          u[10]
        )
      ]) : {};
      l.$set(f);
      const o = {};
      s & /*value*/
      1 && (o.value = /*value*/
      u[0]), s & /*label*/
      16 && (o.label = /*label*/
      u[4]), s & /*show_label*/
      32 && (o.show_label = /*show_label*/
      u[5]), s & /*show_download_button*/
      64 && (o.show_download_button = /*show_download_button*/
      u[6]), s & /*gradio*/
      16384 && (o.i18n = /*gradio*/
      u[14].i18n), e.$set(o);
    },
    i(u) {
      n || (E(l.$$.fragment, u), E(e.$$.fragment, u), n = !0);
    },
    o(u) {
      S(l.$$.fragment, u), S(e.$$.fragment, u), n = !1;
    },
    d(u) {
      u && se(t), L(l, u), L(e, u);
    }
  };
}
function Gl(a) {
  let l, t, e, n;
  const i = [Ul, Dl], r = [];
  function u(s, f) {
    return (
      /*interactive*/
      s[11] ? 1 : 0
    );
  }
  return l = u(a), t = r[l] = i[l](a), {
    c() {
      t.c(), e = Se();
    },
    l(s) {
      t.l(s), e = Se();
    },
    m(s, f) {
      r[l].m(s, f), re(s, e, f), n = !0;
    },
    p(s, [f]) {
      let o = l;
      l = u(s), l === o ? r[l].p(s, f) : (El(), S(r[o], 1, 1, () => {
        r[o] = null;
      }), Bl(), t = r[l], t ? t.p(s, f) : (t = r[l] = i[l](s), t.c()), E(t, 1), t.m(e.parentNode, e));
    },
    i(s) {
      n || (E(t), n = !0);
    },
    o(s) {
      S(t), n = !1;
    },
    d(s) {
      s && se(e), r[l].d(s);
    }
  };
}
function Ll(a, l, t) {
  let { elem_id: e = "" } = l, { elem_classes: n = [] } = l, { visible: i = !0 } = l, { value: r = null } = l, { label: u } = l, { show_label: s } = l, { show_download_button: f } = l, { container: o = !0 } = l, { scale: _ = null } = l, { min_width: w = void 0 } = l, { loading_status: b } = l, { interactive: k } = l, { root: h } = l, { placeholder: U = void 0 } = l, { gradio: c } = l, g;
  const p = () => c.dispatch("clear_status", b), v = () => c.dispatch("clear_status", b), d = (...m) => c.client.upload(...m), Oe = (...m) => c.client.stream(...m);
  function We(m) {
    r = m, t(0, r);
  }
  const Ae = () => c.dispatch("clear"), Fe = ({ detail: m }) => t(15, g = m), He = () => c.dispatch("upload");
  return a.$$set = (m) => {
    "elem_id" in m && t(1, e = m.elem_id), "elem_classes" in m && t(2, n = m.elem_classes), "visible" in m && t(3, i = m.visible), "value" in m && t(0, r = m.value), "label" in m && t(4, u = m.label), "show_label" in m && t(5, s = m.show_label), "show_download_button" in m && t(6, f = m.show_download_button), "container" in m && t(7, o = m.container), "scale" in m && t(8, _ = m.scale), "min_width" in m && t(9, w = m.min_width), "loading_status" in m && t(10, b = m.loading_status), "interactive" in m && t(11, k = m.interactive), "root" in m && t(12, h = m.root), "placeholder" in m && t(13, U = m.placeholder), "gradio" in m && t(14, c = m.gradio);
  }, a.$$.update = () => {
    a.$$.dirty & /*value, gradio*/
    16385 && c.dispatch("change");
  }, [
    r,
    e,
    n,
    i,
    u,
    s,
    f,
    o,
    _,
    w,
    b,
    k,
    h,
    U,
    c,
    g,
    p,
    v,
    d,
    Oe,
    We,
    Ae,
    Fe,
    He
  ];
}
class Wl extends vl {
  constructor(l) {
    super(), Sl(this, l, Ll, Gl, Cl, {
      elem_id: 1,
      elem_classes: 2,
      visible: 3,
      value: 0,
      label: 4,
      show_label: 5,
      show_download_button: 6,
      container: 7,
      scale: 8,
      min_width: 9,
      loading_status: 10,
      interactive: 11,
      root: 12,
      placeholder: 13,
      gradio: 14
    });
  }
  get elem_id() {
    return this.$$.ctx[1];
  }
  set elem_id(l) {
    this.$$set({ elem_id: l }), $();
  }
  get elem_classes() {
    return this.$$.ctx[2];
  }
  set elem_classes(l) {
    this.$$set({ elem_classes: l }), $();
  }
  get visible() {
    return this.$$.ctx[3];
  }
  set visible(l) {
    this.$$set({ visible: l }), $();
  }
  get value() {
    return this.$$.ctx[0];
  }
  set value(l) {
    this.$$set({ value: l }), $();
  }
  get label() {
    return this.$$.ctx[4];
  }
  set label(l) {
    this.$$set({ label: l }), $();
  }
  get show_label() {
    return this.$$.ctx[5];
  }
  set show_label(l) {
    this.$$set({ show_label: l }), $();
  }
  get show_download_button() {
    return this.$$.ctx[6];
  }
  set show_download_button(l) {
    this.$$set({ show_download_button: l }), $();
  }
  get container() {
    return this.$$.ctx[7];
  }
  set container(l) {
    this.$$set({ container: l }), $();
  }
  get scale() {
    return this.$$.ctx[8];
  }
  set scale(l) {
    this.$$set({ scale: l }), $();
  }
  get min_width() {
    return this.$$.ctx[9];
  }
  set min_width(l) {
    this.$$set({ min_width: l }), $();
  }
  get loading_status() {
    return this.$$.ctx[10];
  }
  set loading_status(l) {
    this.$$set({ loading_status: l }), $();
  }
  get interactive() {
    return this.$$.ctx[11];
  }
  set interactive(l) {
    this.$$set({ interactive: l }), $();
  }
  get root() {
    return this.$$.ctx[12];
  }
  set root(l) {
    this.$$set({ root: l }), $();
  }
  get placeholder() {
    return this.$$.ctx[13];
  }
  set placeholder(l) {
    this.$$set({ placeholder: l }), $();
  }
  get gradio() {
    return this.$$.ctx[14];
  }
  set gradio(l) {
    this.$$set({ gradio: l }), $();
  }
}
export {
  Ml as BaseExample,
  jl as BaseImageUploader,
  Pl as BaseStaticImage,
  Wl as default
};
