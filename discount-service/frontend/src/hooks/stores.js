import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: (user, token) => set({ user, token, isAuthenticated: true }),
      logout: () => set({ user: null, token: null, isAuthenticated: false }),
      updateUser: (userData) => set((state) => ({ 
        user: { ...state.user, ...userData } 
      })),
    }),
    {
      name: 'auth-storage',
    }
  )
)

export const useDiscountStore = create((set) => ({
  discounts: [],
  favorites: [],
  collections: [],
  filters: {
    category: null,
    store: null,
    minDiscount: 0,
    search: '',
  },
  
  setDiscounts: (discounts) => set({ discounts }),
  addFavorite: (id) => set((state) => ({ 
    favorites: [...state.favorites, id] 
  })),
  removeFavorite: (id) => set((state) => ({ 
    favorites: state.favorites.filter(fav => fav !== id) 
  })),
  setFilters: (filters) => set((state) => ({ 
    filters: { ...state.filters, ...filters } 
  })),
  resetFilters: () => set({ 
    filters: {
      category: null,
      store: null,
      minDiscount: 0,
      search: '',
    }
  }),
}))

export const useFamilyCardStore = create(
  persist(
    (set) => ({
      familyCard: null,
      members: [],
      
      setFamilyCard: (card) => set({ familyCard: card }),
      addMember: (member) => set((state) => ({ 
        members: [...state.members, member] 
      })),
      removeMember: (memberId) => set((state) => ({ 
        members: state.members.filter(m => m.id !== memberId) 
      })),
    }),
    {
      name: 'family-card-storage',
    }
  )
)

export const useUIStore = create((set) => ({
  isMobileMenuOpen: false,
  currentTab: 'home',
  theme: 'light',
  
  toggleMobileMenu: () => set((state) => ({ 
    isMobileMenuOpen: !state.isMobileMenuOpen 
  })),
  setTab: (tab) => set({ currentTab: tab }),
  setTheme: (theme) => set({ theme }),
}))
