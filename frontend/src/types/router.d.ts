import 'vue-router'

import type { RoleType } from '@/types'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    roles?: RoleType[]
    menu?: boolean
    icon?: string
    public?: boolean
  }
}

export {}
